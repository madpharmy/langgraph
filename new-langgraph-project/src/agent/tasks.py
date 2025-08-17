from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, TypedDict

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

from agent.config import Settings
from agent.services import fetch_odds_events, fetch_odds_markets, fetch_espn_scoreboard


class Context(TypedDict, total=False):
    settings: Settings


# Events task
@dataclass
class EventsState:
    sport_key: str
    region: str = "us"
    result: Optional[dict] = None


async def events_node(state: EventsState, runtime: Runtime[Context]) -> Dict[str, Any]:
    cfg = runtime.context.get("settings") or Settings.load()
    if not cfg.odds_api_key:
        return {"result": {"error": "ODDS_API_KEY not set"}}
    data = fetch_odds_events(cfg.odds_api_key, state.sport_key, region=state.region, timeout=cfg.http_timeout_s, retries=cfg.http_retries)
    return {"result": data}


events_graph = (
    StateGraph(EventsState, context_schema=Context)
    .add_node(events_node)
    .add_edge("__start__", "events_node")
    .compile(name="Events Task")
)


# Markets task
@dataclass
class MarketsState:
    sport_key: str
    event_id: str
    markets: str = "h2h,spreads,totals"
    region: str = "us"
    result: Optional[dict] = None


async def markets_node(state: MarketsState, runtime: Runtime[Context]) -> Dict[str, Any]:
    cfg = runtime.context.get("settings") or Settings.load()
    if not cfg.odds_api_key:
        return {"result": {"error": "ODDS_API_KEY not set"}}
    data = fetch_odds_markets(
        cfg.odds_api_key,
        state.sport_key,
        state.event_id,
        markets=state.markets,
        region=state.region,
        timeout=cfg.http_timeout_s,
        retries=cfg.http_retries,
    )
    return {"result": data}


markets_graph = (
    StateGraph(MarketsState, context_schema=Context)
    .add_node(markets_node)
    .add_edge("__start__", "markets_node")
    .compile(name="Markets Task")
)


# Sports data task
@dataclass
class SportsDataState:
    league_path: str = "basketball/nba/scoreboard"
    result: Optional[dict] = None


async def sports_data_node(state: SportsDataState, runtime: Runtime[Context]) -> Dict[str, Any]:
    cfg = runtime.context.get("settings") or Settings.load()
    data = fetch_espn_scoreboard(state.league_path, timeout=cfg.http_timeout_s, retries=cfg.http_retries)
    return {"result": data}


sports_data_graph = (
    StateGraph(SportsDataState, context_schema=Context)
    .add_node(sports_data_node)
    .add_edge("__start__", "sports_data_node")
    .compile(name="Sports Data Task")
)
