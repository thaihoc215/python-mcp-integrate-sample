# HTTP SSE MCP Demo

A demonstration project for HTTP Server-Sent Events with Mission Control Protocol integration.

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) - Python package installer and virtual environment manager
- Setup Zapier action (send gmail email / Jira create issue / etc.)

## Setup

1. Create a virtual environment:
```bash
uv venv
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install additional packages:
```bash
uv add mcp openai python-dotenv
```

To install all requirements using `uv`, run the following command in your terminal:

```
uv pip install -r requirements.txt
```

Make sure you have a requirements.txt file in your project directory. If you don’t have `uv` installed, you can install it with:

```
pip install uv
```

Let me know if you need help with anything else!

## Running the Application

### Run Zapier Integration Client
```bash
uv run -- client_zapier_openapi.py
```

```bash
uv run -- client_zapier_list_tools.py
```

## Example Use Cases Promt

- Add a comment to a JIRA ticket:
  ```
  comment to jira ticket: FE-2018 with comment: comment from mcp client
  ```

- Send an email report:
  ```
  Send an email with the subject 'Weekly Report' and a message about recent project updates.
  ```


- https://github.com/modelcontextprotocol/python-sdk/blob/main/README.md

## Q&A

---

**Q: With streamable, with stateless server, do we really need to call `await session.initialize()`?**

**A:**
Yes, you still need to call `await session.initialize()` even when using a stateless server with the streamable HTTP transport.

**Why?**
- The MCP protocol requires an explicit initialization handshake between the client and the server, regardless of whether the server is stateful or stateless.
- The `initialize()` call negotiates protocol features, capabilities, and ensures the session (even if ephemeral and stateless) is ready for subsequent requests like `call_tool`, `list_tools`, etc.
- The streamable HTTP client example in the README specifically includes `await session.initialize()` in the code, for both stateful and stateless servers.

**Example:**
```python
async with streamablehttp_client("example/mcp") as (read_stream, write_stream, _):
    async with ClientSession(read_stream, write_stream) as session:
        # Initialize the connection
        await session.initialize()
        # Call a tool
        tool_result = await session.call_tool("echo", {"message": "hello"})
```

**Summary:**
Even with stateless servers and the streamable HTTP transport, `await session.initialize()` is required before making other API calls. Skipping it may cause requests to fail or behave unexpectedly.

---

**Q: What is the difference between stateful and stateless server if I have to call `await session.initialize()` in both cases?**

**A:**
Great question! The difference between stateful and stateless MCP servers is not about whether you call `await session.initialize()`—that is a protocol requirement in both cases. The distinction is about how the server handles session data, context, and continuity between requests.

### Stateful Server
- **Keeps session state:** The server remembers your session context (such as authentication, temporary data, or ongoing conversation) between requests.
- **Connection-oriented:** Typically, you have a persistent connection (like a WebSocket or a long-lived HTTP stream), and the server can associate all your actions with your session.
- **Session continuity:** Things like progress updates, streamed results, or background tasks can be tied to your session.
- **Example:** Classic WebSocket or SSE MCP server, or streamable HTTP with session persistence.

### Stateless Server
- **Does NOT keep session state:** The server treats each request independently. It does not remember anything about previous requests from the same client.
- **Request-oriented:** Each request must contain all the necessary context, because the server doesn’t know what happened before.
- **No session continuity:** Things like partial progress, ongoing tasks, or in-memory data across calls are not possible.
- **Example:** Streamable HTTP server with `stateless_http=True` or `json_response=True` (as shown in the README).

### Why do you need `await session.initialize()` in both?
- **Protocol handshake:** The MCP protocol requires an explicit initialization handshake, even for stateless servers. This step lets the server declare its capabilities, available tools/resources/prompts, and negotiate protocol features for the current request or ephemeral session.
- **Client setup:** The client needs to know what it can do (what tools/resources are available, how to call them, etc.), and the only way to ensure this is to call `initialize()`.

### Practical difference (summary)
- **Stateful:** The server can store and rely on your session data between calls.
- **Stateless:** The server forgets everything after each call—each API call is independent.
- **`await session.initialize()` is still required** for protocol compliance and discovery, but it does *not* imply the server will remember you between requests in stateless mode.

---

**In short:**
You must call `await session.initialize()` for both, but only stateful servers keep data and context between requests. Stateless servers require you to provide all necessary info with each call, as they forget everything between requests. The initialization step is just a protocol handshake, not a guarantee of session persistence.