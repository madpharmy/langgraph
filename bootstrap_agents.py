#!/usr/bin/env python3
"""Bootstrap launcher for the unified Project Dashboard (single venv).

This replaced an old RAG bootstrap that referenced a non-existent
``rag_pipeline`` module. We now steer operators to the Streamlit
dashboard which includes:

- Overview: env keys, installed packages, graphs from langgraph.json
- Logs: a built-in log viewer to follow .log files live

Run this script from Windows to launch the dashboard automatically.
Otherwise it will try to open the expected dashboard URL.
"""

from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from pathlib import Path


DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8592"))
TEMPLATE_DIR = Path(__file__).resolve().parent / "new-langgraph-project"
PS1_DASHBOARD = TEMPLATE_DIR / "scripts" / "dashboard_windows.ps1"


def launch_windows_dashboard(port: int) -> bool:
    """Launch the Windows dashboard script if available."""
    try:
        if PS1_DASHBOARD.exists():
            subprocess.Popen(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(PS1_DASHBOARD),
                    "-Port",
                    str(port),
                ],
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,  # type: ignore[attr-defined]
            )
            return True
    except Exception:
        pass
    return False


def main() -> int:
    url = f"http://127.0.0.1:{DASHBOARD_PORT}"
    launched = False
    if os.name == "nt":
        launched = launch_windows_dashboard(DASHBOARD_PORT)
    # Open the expected URL either way
    try:
        webbrowser.open(url)
    except Exception:
        pass
    if not launched:
        print(
            "Dashboard not auto-launched. Run 'start_all_windows.cmd' or "
            f"'new-langgraph-project\\scripts\\dashboard_windows.cmd -Port {DASHBOARD_PORT}'."
        )
    else:
        print(f"Dashboard launching at {url} …")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
