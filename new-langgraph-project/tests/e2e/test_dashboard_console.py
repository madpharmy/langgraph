import os
import time
import pytest
from playwright.sync_api import expect


DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://127.0.0.1:8592")


@pytest.mark.e2e
def test_console_runs_command_and_shows_output(page):
    # Start Playwright tracing for debugging on failures
    page.context.tracing.start(screenshots=True, snapshots=True, sources=True)
    try:
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=120_000)

        # Open the Console tab (sidebar radio option)
        page.get_by_text("Console", exact=True).first.click()

        # Enter a simple command and run
        cmd = "echo hello-e2e"
        page.get_by_label("PowerShell command").fill(cmd)
        page.locator("[data-testid='btn-run-command']").locator("xpath=following::button[1]").click()

        # Nudge UI to refresh quickly and keep tail small
        try:
            page.get_by_label("Refresh (s)").fill("1")
        except Exception:
            pass
        try:
            page.get_by_label("Tail lines").fill("200")
        except Exception:
            pass
        # Force a refresh to avoid flakiness, then wait for text
        try:
            page.locator("[data-testid='btn-refresh-now']").locator("xpath=following::button[1]").click()
        except Exception:
            page.wait_for_timeout(1000)
        page.wait_for_function(
            "() => { const el = document.querySelector('[data-testid=\\'console-output\\']'); return !!(el && el.innerText && el.innerText.includes('hello-e2e')); }",
            timeout=20000,
        )
    finally:
        # Save Playwright trace for diagnostics
        try:
            from pathlib import Path
            repo_root = Path(__file__).resolve().parents[3]
            out = repo_root / 'logs' / 'dashboard_console_trace.zip'
            out.parent.mkdir(parents=True, exist_ok=True)
            page.context.tracing.stop(path=str(out))
        except Exception:
            pass
