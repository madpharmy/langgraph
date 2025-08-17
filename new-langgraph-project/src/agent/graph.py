"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, TypedDict

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime


class Context(TypedDict):
    """Context parameters for the agent.

    Set these when creating assistants OR when invoking the graph.
    See: https://langchain-ai.github.io/langgraph/cloud/how-tos/configuration_cloud/
    """

    my_configurable_param: str


@dataclass
class State:
    """Input state for the agent.

    Defines the initial structure of incoming data.
    See: https://langchain-ai.github.io/langgraph/concepts/low_level/#state
    """

    changeme: str = "example"


def call_model(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Process input and returns output.

    Can use runtime context to alter behavior.
    """
    return {
        "changeme": "output from call_model. "
        f"Configured with {runtime.context.get('my_configurable_param')}"
    }


# Define the graph
graph = (
    StateGraph(State, context_schema=Context)
    .add_node(call_model)
    .add_edge("__start__", "call_model")
    .compile(name="New Graph")
)

# ---- mem0 integration graphs (optional) ----
try:
    from mem0_mcp import store as _mem0_store  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    _mem0_store = None  # type: ignore


@dataclass
class MemListState:
    pass


def mem_list_node(state: MemListState, runtime: Runtime[Context]) -> Dict[str, Any]:
    if _mem0_store is None:
        return {"error": "mem0_mcp not installed. Install D:/mem0 or pip install mem0-mcp."}
    data = _mem0_store.load_mem()
    titles = [n.get("title", "(untitled)") for n in data.get("notes", [])]
    return {"notes": titles}


mem_list_graph = (
    StateGraph(MemListState, context_schema=Context)
    .add_node(mem_list_node)
    .add_edge("__start__", "mem_list_node")
    .compile(name="Mem0 List Notes")
)


@dataclass
class MemDumpState:
    pass


def mem_dump_node(state: MemDumpState, runtime: Runtime[Context]) -> Dict[str, Any]:
    if _mem0_store is None:
        return {"error": "mem0_mcp not installed. Install D:/mem0 or pip install mem0-mcp."}
    return {"mem": _mem0_store.load_mem()}


mem_dump_graph = (
    StateGraph(MemDumpState, context_schema=Context)
    .add_node(mem_dump_node)
    .add_edge("__start__", "mem_dump_node")
    .compile(name="Mem0 Dump JSON")
)


@dataclass
class MemAddState:
    title: str
    content: str
    tags: str = ""


def mem_add_node(state: MemAddState, runtime: Runtime[Context]) -> Dict[str, Any]:
    if _mem0_store is None:
        return {"error": "mem0_mcp not installed. Install D:/mem0 or pip install mem0-mcp."}
    tag_list = [t.strip() for t in (state.tags or "").split(",") if t.strip()]
    _mem0_store.add_note(state.title or "(untitled)", state.content or "", tag_list)
    return {"ok": True, "title": state.title}


mem_add_graph = (
    StateGraph(MemAddState, context_schema=Context)
    .add_node(mem_add_node)
    .add_edge("__start__", "mem_add_node")
    .compile(name="Mem0 Add Note")
)
