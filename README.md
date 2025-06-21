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

