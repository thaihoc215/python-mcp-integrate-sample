# client.py
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    url = "http://127.0.0.1:8000/mcp"
    async with streamablehttp_client(url) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            # await session.initialize()            # JSON-RPC „initialize“
            
            # list tools and print them
            tools = await session.list_tools()    # JSON-RPC „list_tools“
            print(f"Available tools: {tools}")
            # for tool in tools:
            #     print(f" * {tool.name} - {tool.description}")
            result = await session.call_tool("add", {"a": 21, "b": 21})
            print("Result from server:", result)

if __name__ == "__main__":
    asyncio.run(main())
