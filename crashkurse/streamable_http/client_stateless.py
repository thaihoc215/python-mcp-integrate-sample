# client.py
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    url = os.getenv("ZAPIER_STREAMABLE_URL", "http://127.0.0.1:8000/mcp")
    try:
        async with streamablehttp_client(url) as (read, write, get_session_id):
            print(f"Connecting to Streamable HTTP MCP server at: {url}")
            async with ClientSession(read, write) as session:
                # await session.initialize()            # JSON-RPC „initialize“
                
                # list tools and print them
                tools = await session.list_tools()    # JSON-RPC „list_tools“
                print(f"Available tools: {tools}")
                # for tool in tools:
                #     print(f" * {tool.name} - {tool.description}")
                if os.getenv("ZAPIER_STREAMABLE_TEST_ADD", ""):
                    result = await session.call_tool("add", {"a": 21, "b": 21})
                    print("Result from server:", result)
                else:
                    arguments = {
                        "instructions": "Send a test email to xxx@gmail.com with subject and body.",
                        "subject": "Test Email from MCP Client 123",
                        "body": "This is a test email sent through the Zapier MCP integration 123."
                    }
                    result = await session.call_tool("gmail_send_email", arguments)
                    print("Result from server:", result)
                    pass
    except* Exception as eg:  # Python 3.11+ ExceptionGroup handling
        print(f"ExceptionGroup occurred: {eg}")
        for exc in eg.exceptions:
            print(f"  Sub-exception: {exc}")
            # print type of exception
            print(f"  Exception type: {type(exc)}")
            if hasattr(exc, 'response') and hasattr(exc.response, 'status_code'):
                if exc.response.status_code == 401:
                    print("Authentication failed. Please check your ZAPIER_STREAMABLE_URL or API credentials.")
                else:
                    print(f"HTTP error occurred: {exc.response.status_code}")
            elif "401 Unauthorized" in str(exc):
                print("Authentication failed. Please check your ZAPIER_STREAMABLE_URL or API credentials.")
            elif "HTTPStatusError" in str(exc):
                print("HTTP error occurred. Please check the server URL and network connectivity.")
            else:
                print("An unexpected error occurred in a task.")
    return
    # except Exception as e:
    #     print(f"Error connecting to MCP server: {e}")
    #     if "401 Unauthorized" in str(e):
    #         print("Authentication failed. Please check your ZAPIER_STREAMABLE_URL or API credentials.")
    #     elif "HTTPStatusError" in str(e):
    #         print("HTTP error occurred. Please check the server URL and network connectivity.")
    #     else:
    #         print("An unexpected error occurred.")
    #     return


if __name__ == "__main__":
    asyncio.run(main())
