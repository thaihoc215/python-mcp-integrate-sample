import asyncio
import os
import sys
import traceback
from dotenv import load_dotenv
import openai
import json
from urllib.parse import urlparse

from mcp import ClientSession
from mcp.client.sse import sse_client

load_dotenv()

async def main():
    
    zapier_mcp_url = os.getenv("ZAPIER_MCP_URL", "http://localhost:8000/sse")
    openai.api_key = os.getenv("OPENAI_API_KEY")

    try:
        # Example: Add a comment to Jira
        # jira_tool_name = "jira_software_cloud_add_comment_"
        # jira_args = {
        #     "issueKey": "FE-2018",  # Replace with your actual issue key
        #     "comment": "This is a test comment added via MCP integration"
        # }
        
        # result = await execute_mcp_tool(zapier_mcp_url, jira_tool_name, jira_args)
        # print("Tool result:", result)

        tools_sample = [
            {
                "type": "function",
                "function": {
                    "name": "gmail_send_email",
                    "description": "Create and send a new email message. (Fixed parameters: To)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "subject": {
                                "type": "string",
                                "description": "Subject"
                            },
                            "body": {
                                "type": "string",
                                "description": "Body"
                            }
                        },
                        "required": ["subject", "body"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "jira_software_cloud_add_comment_",
                    "description": "Adds a new comment to an issue.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "issueKey": {
                                "type": "string",
                                "description": "Issue"
                            },
                            "comment": {
                                "type": "string",
                                "description": "Comment"
                            }
                        },
                        "required": ["issueKey", "comment"]
                    }
                }
            }
        ]

        # Get available tools from MCP server
        mcp_tools = await get_mcp_available_tools(zapier_mcp_url)
        print("Available MCP tools:", mcp_tools)

        tools = convert_mcp_tools_to_openai_format(mcp_tools)
        # Define user prompt
        # user_prompt = "Send an email with the subject 'Weekly Report' and a message about recent project updates."
        while True:
            user_prompt = input("Enter your prompt: ")
            if user_prompt.lower() == 'exit':
                print("Exiting program.")
                break

            open_ai_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that can perform actions using external tools."},
                    {"role": "user", "content": user_prompt}
                ],
                tools=tools
            )
            message = open_ai_response.choices[0].message
            print("Message :", message)

            if message and message.tool_calls:
                tool_call = message.tool_calls[0]
                function_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print("openAI response function_name:", function_name)
                print("openAI response args:", args)
                async with sse_client(url=zapier_mcp_url) as (read, write):
                    # Create and use a client session
                    print("sse_client", zapier_mcp_url)
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        # zap_tools = await session.list_tools()
                        # print("Available tools:", zap_tools)
                
                        try:
                            result = await session.call_tool(function_name, args)
                            print("Tool result:", result)
                        except Exception as tool_exc:
                            print(f"Error calling {function_name}:")
                            traceback.print_exception(
                                type(tool_exc), tool_exc, tool_exc.__traceback__
                            )
            else:
                print(f"LLM response: {message.content}")

    

        # Call the tool using the MCP client
        # result = await execute_mcp_tool(zapier_mcp_url, function_name, args)
        # print("Tool result:", result)

        # async with sse_client(url=zapier_mcp_url) as (read, write):
        #     # Create and use a client session
        #     print("sse_client", zapier_mcp_url)
        #     async with ClientSession(read, write) as session:
        #         await session.initialize()
        #         zapTools = await session.list_tools()
        #         print("Available tools:", zapTools)
        #
        #
        #
        #         # tool_name = "gmail_send_email"
        #         # arguments = {
        #         #     "subject": "Test Email from MCP Client",
        #         #     "body": "This is a test email sent through the Zapier MCP integration."
        #         # }
        #         try:
        #             result = await session.call_tool(function_name, args)
        #             print("Tool result:", result)
        #         except Exception as tool_exc:
        #             print(f"Error calling {function_name}:")
        #             traceback.print_exception(
        #                 type(tool_exc), tool_exc, tool_exc.__traceback__
        #             )

                

        
    except Exception as e:
        print(f"Error executing to server: {e}")
        traceback.print_exception(type(e), e, e.__traceback__)
        sys.exit(1)


async def execute_mcp_tool(mcp_url, tool_name, arguments):
    """Execute a tool using MCP client.
    
    Args:
        mcp_url: URL to the MCP server endpoint
        tool_name: Name of the tool to execute
        arguments: Dictionary of arguments to pass to the tool
        
    Returns:
        The result of the tool execution
    """
    try:
        print(f"Connecting to MCP server at {mcp_url}")
        print(f"Executing tool: {tool_name}")
        print(f"With arguments: {json.dumps(arguments, indent=2)}")

        async with sse_client(url=mcp_url) as (read, write):
            # Create and use a client session
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Optionally list available tools
                tools = await session.list_tools()
                print("Available tools:", tools)

                # Execute the requested tool
                result = await session.call_tool(tool_name, arguments)
                print(f"Tool execution successful: {tool_name}")
                return result

    except Exception as e:
        print(f"Error executing tool {tool_name}:")
        traceback.print_exception(type(e), e, e.__traceback__)
        raise

async def get_mcp_available_tools(mcp_url):
    """Get available tools from an MCP server.
    
    Args:
        mcp_url: URL to the MCP server endpoint
        
    Returns:
        List of available tools from the MCP server
    """
    try:
        print(f"Connecting to MCP server at {mcp_url} to fetch available tools...")
        
        async with sse_client(url=mcp_url) as (read, write):
            # Create and use a client session
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Get available tools
                tools = await session.list_tools()
                print(f"Successfully retrieved {len(tools.tools) if tools.tools else 0} tools from MCP server")
                return tools
                
    except Exception as e:
        print(f"Error retrieving tools from MCP server:")
        traceback.print_exception(type(e), e, e.__traceback__)
        raise

def convert_mcp_tools_to_openai_format(mcp_tools):
    """Convert MCP tools format to OpenAI function format.
    
    Args:
        mcp_tools: Tools object returned from MCP's list_tools() method
        
    Returns:
        List of tools in OpenAI function format
    """
    if not mcp_tools or not mcp_tools.tools:
        print("No MCP tools available to convert")
        return []
    
    openai_tools = []
    
    for tool in mcp_tools.tools:
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        
        # Extract properties and required fields from inputSchema
        if hasattr(tool, 'inputSchema') and tool.inputSchema:
            # Copy over the properties
            if 'properties' in tool.inputSchema:
                openai_tool["function"]["parameters"]["properties"] = tool.inputSchema['properties']
            
            # Copy over required fields
            if 'required' in tool.inputSchema:
                openai_tool["function"]["parameters"]["required"] = tool.inputSchema['required']
        
        openai_tools.append(openai_tool)
    
    print(f"Successfully converted {len(openai_tools)} MCP tools to OpenAI format")
    print("Converted tools:", json.dumps(openai_tools, indent=2))
    return openai_tools

if __name__ == "__main__":
    print("sys.argv:", sys.argv)
    print("Number of arguments:", len(sys.argv))
    asyncio.run(main())
