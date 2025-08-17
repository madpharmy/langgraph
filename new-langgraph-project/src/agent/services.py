from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx


log = logging.getLogger(__name__)


def _with_retries(client: httpx.Client, method: str, url: str, *, retries: int = 2, **kw: Any) -> httpx.Response:
    last_err: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            resp = client.request(method, url, **kw)
            resp.raise_for_status()
            return resp
        except Exception as e:  # pragma: no cover
            last_err = e
            log.warning("http_retry", extra={"attempt": attempt, "url": url})
    assert last_err is not None
    raise last_err


def fetch_odds_events(api_key: str, sport_key: str, region: str = "us", timeout: float = 20.0, retries: int = 2) -> Dict[str, Any]:
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/events"
    params = {"apiKey": api_key, "regions": region, "dateFormat": "iso"}
    with httpx.Client(timeout=timeout) as client:
        resp = _with_retries(client, "GET", url, retries=retries, params=params)
        data = resp.json()
    # Minimal normalization
    events = []
    for e in data or []:
        events.append(
            {
                "id": e.get("id", ""),
                "sport_key": e.get("sport_key"),
                "commence_time": e.get("commence_time"),
                "home_team": e.get("home_team"),
                "away_team": e.get("away_team"),
            }
        )
    return {"events": events}


def fetch_odds_markets(api_key: str, sport_key: str, event_id: str, markets: str = "h2h,spreads,totals", region: str = "us", timeout: float = 20.0, retries: int = 2) -> Dict[str, Any]:
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/events/{event_id}/odds"
    params = {"apiKey": api_key, "regions": region, "markets": markets, "dateFormat": "iso"}
    with httpx.Client(timeout=timeout) as client:
        resp = _with_retries(client, "GET", url, retries=retries, params=params)
        data = resp.json()
    out_markets = []
    for bk in (data or {}).get("bookmakers", []) or []:
        title = bk.get("title") or bk.get("key")
        for mk in bk.get("markets", []) or []:
            out_markets.append(
                {
                    "bookmaker": title,
                    "market": mk.get("key"),
                    "outcomes": [
                        {"name": o.get("name"), "price": o.get("price"), "point": o.get("point")}
                        for o in mk.get("outcomes", []) or []
                    ],
                }
            )
    return {"event_id": data.get("id"), "sport_key": data.get("sport_key"), "markets": out_markets}


def fetch_espn_scoreboard(league_path: str, timeout: float = 20.0, retries: int = 2) -> Dict[str, Any]:
    base = "https://site.api.espn.com/apis/site/v2/sports"
    url = f"{base}/{league_path}"
    with httpx.Client(timeout=timeout) as client:
        resp = _with_retries(client, "GET", url, retries=retries)
        data = resp.json()
    games = []
    for ev in (data or {}).get("events", []) or []:
        competitions = ev.get("competitions", []) or []
        status = (competitions[0].get("status", {}) or {}).get("type", {}).get("description") if competitions else None
        comp_list = []
        if competitions:
            for c in competitions[0].get("competitors", []) or []:
                comp_list.append(
                    {
                        "name": (c.get("team", {}) or {}).get("displayName"),
                        "score": c.get("score"),
                        "homeAway": c.get("homeAway"),
                    }
                )
        games.append(
            {
                "id": ev.get("id"),
                "date": ev.get("date"),
                "name": ev.get("name"),
                "shortName": ev.get("shortName"),
                "status": status,
                "competitors": comp_list,
            }
        )
    return {"games": games}

