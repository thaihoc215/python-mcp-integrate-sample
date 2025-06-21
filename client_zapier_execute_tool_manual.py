import asyncio
import sys
import traceback
from dotenv import load_dotenv
import os

from mcp import ClientSession
from mcp.client.sse import sse_client

load_dotenv()


def print_items(name: str, result: any) -> None:
    """Print items with formatting.

    Args:
        name: Category name (tools/resources/prompts)
        result: Result object containing items list
    """
    print(f"\nAvailable {name}:")
    items = getattr(result, name)
    if items:
        for item in items:
            print(" *", item)
    else:
        print("No items available")


async def main():
# async def main(server_url: str, article_url: str = None):
    """Connect to the MCP server, list its capabilities, and optionally call a tool.

    Args:
        server_url: Full URL to SSE endpoint (e.g. http://localhost:8000/sse)
        article_url: (Optional) Wikipedia URL to fetch an article
    """
    # if urlparse(server_url).scheme not in ("http", "https"):
    #     print("Error: Server URL must start with http:// or https://")
    #     sys.exit(1)

    # Replace with your actual Zapier MCP server URL
    zapier_mcp_url = os.getenv("ZAPIER_MCP_URL", "http://localhost:8000/sse")
    

    try:
        # Create SSE client streams
        async with sse_client(url=zapier_mcp_url) as (read, write):
            # Create and use a client session
            print("sse_client: ", zapier_mcp_url)
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("Available tools:", await session.list_tools())
                # print("Available promts:", await session.list_prompts())
                # print("Available resources:", await session.list_resources())

                # Example: Call a tool (adjust based on available tools)
                tool_name = "gmail_send_email"
                arguments = {
                    "instructions": "Send a test email to HaThaiHoc.Nguyen@lofty.com using the MCP Zapier integration.",
                    "to": "HaThaiHoc.Nguyen@lofty.com",
                    "subject": "Test Email from MCP Client",
                    "body": "This is a test email sent through the Zapier MCP integration."
                }
                try:
                    result = await session.call_tool(tool_name, arguments)
                    print("Tool result:", result)
                except Exception as tool_exc:
                    print(f"Error calling {tool_name}:")
                    traceback.print_exception(
                        type(tool_exc), tool_exc, tool_exc.__traceback__
                    )
    except Exception as e:
        print(f"Error connecting to server: {e}")
        traceback.print_exception(type(e), e, e.__traceback__)
        sys.exit(1)


if __name__ == "__main__":
    print("sys.argv:", sys.argv)
    print("Number of arguments:", len(sys.argv))
    # if len(sys.argv) < 2:
    #     print(
    #         "Usage: uv run -- client.py <server_url> [<wikipedia_article_url>]\n"
    #         "Example: uv run -- client.py http://localhost:8000/sse https://en.wikipedia.org/wiki/Python_(programming_language)"
    #     )
    #     sys.exit(1)

    # server_url = sys.argv[1]
    # article_url = sys.argv[2] if len(sys.argv) > 2 else None
    # asyncio.run(main(server_url, article_url))
    asyncio.run(main())
