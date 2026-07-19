"""
tools.py

All tools used by the agent.
"""

from langchain_core.tools import tool


@tool
def search_tool(query: str) -> str:
    """
    Search tool.
    """

    return f"Search results for: {query}"


@tool
def send_email_tool(
    to: str,
    body: str,
) -> str:
    """
    Email tool.
    """

    return f"Email successfully sent to {to}"


@tool
def general_tool(query: str) -> str:
    """
    General utility tool.
    """

    return f"Processed: {query}"