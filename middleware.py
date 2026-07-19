from typing import Any

from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    hook_config,
)

from langgraph.runtime import Runtime

from langchain_core.messages import AIMessage
from langchain_mistralai import ChatMistralAI


class ContentFilterMiddleware(AgentMiddleware):
    """
    Blocks requests containing banned keywords
    BEFORE they reach the LLM.
    """

    def __init__(self, banned_keywords: list[str]):
        super().__init__()
        self.banned_keywords = [
            keyword.lower()
            for keyword in banned_keywords
        ]

    @hook_config(can_jump_to=["end"])
    def before_agent(
        self,
        state: AgentState,
        runtime: Runtime,
    ) -> dict[str, Any] | None:

        if not state["messages"]:
            return None

        first_message = state["messages"][0]

        if first_message.type != "human":
            return None

        content = first_message.content.lower()

        for keyword in self.banned_keywords:

            if keyword in content:

                print(f"Blocked keyword detected: {keyword}")

                return {
                    "messages": [
                        {
                            "role": "assistant",
                            "content":
                                "I cannot process requests containing "
                                "unsafe or prohibited content."
                        }
                    ],
                    "jump_to": "end",
                }

        return None


class SafetyGuardrailMiddleware(AgentMiddleware):
    """
    Uses a second LLM to judge whether the
    generated response is safe.
    """

    def __init__(self):

        super().__init__()

        self.safety_model = ChatMistralAI(
            model="mistral-small-2506",
            temperature=0,
        )

    @hook_config(can_jump_to=["end"])
    def after_agent(
        self,
        state: AgentState,
        runtime: Runtime,
    ) -> dict[str, Any] | None:

        if not state["messages"]:
            return None

        last_message = state["messages"][-1]

        if not isinstance(last_message, AIMessage):
            return None

        safety_prompt = f"""
You are a safety evaluator.

Determine whether the following AI response is safe.

Reply with ONLY:

SAFE

or

UNSAFE

Response:

{last_message.content}
"""

        result = self.safety_model.invoke(
            [
                {
                    "role": "user",
                    "content": safety_prompt,
                }
            ]
        )

        if "UNSAFE" in result.content.upper():

            print("Unsafe response detected.")

            last_message.content = (
                "I'm unable to provide that response. "
                "Please ask another question."
            )

        return None