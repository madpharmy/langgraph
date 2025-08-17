# New LangGraph Project

[![CI](https://github.com/langchain-ai/new-langgraph-project/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/langchain-ai/new-langgraph-project/actions/workflows/unit-tests.yml)
[![Integration Tests](https://github.com/langchain-ai/new-langgraph-project/actions/workflows/integration-tests.yml/badge.svg)](https://github.com/langchain-ai/new-langgraph-project/actions/workflows/integration-tests.yml)

This template demonstrates a simple application implemented using [LangGraph](https://github.com/langchain-ai/langgraph), designed for showing how to get started with [LangGraph Server](https://langchain-ai.github.io/langgraph/concepts/langgraph_server/#langgraph-server) and using [LangGraph Studio](https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/), a visual debugging IDE.

<div align="center">
  <img src="./static/studio_ui.png" alt="Graph view in LangGraph studio UI" width="75%" />
</div>

The core logic defined in `src/agent/graph.py`, showcases an single-step application that responds with a fixed string and the configuration provided.

You can extend this graph to orchestrate more complex agentic workflows that can be visualized and debugged in LangGraph Studio.

## Getting Started (No WSL Required)

This template runs natively on Windows, macOS, and Linux. On Windows, use PowerShell; no WSL is needed.

### Windows (PowerShell)

1) Create and activate a Python 3.11+ virtual environment

```
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install the project and the LangGraph CLI (in-memory server)

```
pip install -e . "langgraph-cli[inmem]"
```

3) (Optional) Create a `.env` and set keys

```
Copy-Item .env.example .env
# Example (PowerShell):
$env:LANGSMITH_API_KEY = "lsv2..."
```

4) Start the LangGraph server

```
langgraph dev
```

Alternatively, use the helper scripts:

```
scripts\setup_windows.ps1
scripts\dev_windows.ps1 -Host 127.0.0.1 -Port 8124 -DebuggerPort 3001
# Or wrappers if PowerShell scripts are restricted:
scripts\setup_windows.cmd
scripts\dev_windows.cmd -Host 127.0.0.1 -Port 8124 -DebuggerPort 3001

Optional: launch the Project Dashboard (Streamlit):

```
scripts\dashboard_windows.ps1 -Port 8592
# Or wrapper:
scripts\dashboard_windows.cmd -Port 8592
```
```

### macOS/Linux (bash)

1) Install dependencies, along with the [LangGraph CLI](https://langchain-ai.github.io/langgraph/concepts/langgraph_cli/), which will be used to run the server.

```bash
cd path/to/your/app
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e . "langgraph-cli[inmem]"
```

2) (Optional) Customize the code and project as needed. Create a `.env` file if you need to use secrets.

```bash
cp .env.example .env
```

If you want to enable LangSmith tracing, add your LangSmith API key to the `.env` file.

```text
# .env
LANGSMITH_API_KEY=lsv2...
```

3) Start the LangGraph Server.

```shell
langgraph dev
```

For more information on getting started with LangGraph Server, [see here](https://langchain-ai.github.io/langgraph/tutorials/langgraph-platform/local-server/).

## How to customize

1. **Define runtime context**: Modify the `Context` class in the `graph.py` file to expose the arguments you want to configure per assistant. For example, in a chatbot application you may want to define a dynamic system prompt or LLM to use. For more information on runtime context in LangGraph, [see here](https://langchain-ai.github.io/langgraph/agents/context/?h=context#static-runtime-context).

2. **Extend the graph**: The core logic of the application is defined in [graph.py](./src/agent/graph.py). You can modify this file to add new nodes, edges, or change the flow of information.

## Development

While iterating on your graph in LangGraph Studio, you can edit past state and rerun your app from previous states to debug specific nodes. Local changes will be automatically applied via hot reload.

Follow-up requests extend the same thread. You can create an entirely new thread, clearing previous history, using the `+` button in the top right.

For more advanced features and examples, refer to the [LangGraph documentation](https://langchain-ai.github.io/langgraph/). These resources can help you adapt this template for your specific use case and build more sophisticated conversational agents.

LangGraph Studio also integrates with [LangSmith](https://smith.langchain.com/) for more in-depth tracing and collaboration with teammates, allowing you to analyze and optimize your chatbot's performance.
