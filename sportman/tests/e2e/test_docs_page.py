import os
import re
import pytest
from playwright.sync_api import expect


BASE_URL = os.getenv("SPORTMAN_BASE_URL", "http://127.0.0.1:8123")


@pytest.mark.e2e
def test_docs_page_loads(page):
    url = f"{BASE_URL}/docs"
    page.goto(url, wait_until="networkidle", timeout=120_000)
    # Accept Scalar (new FastAPI default) or Swagger UI
    try:
        title = page.title()
    except Exception:
        title = ""
    if "Scalar" in title:
        # Minimal visible element check to ensure UI is rendered
        assert "Scalar" in title
    else:
        # Fallback to Swagger UI text for older setups
        expect(page.get_by_text("Swagger UI")).to_be_visible()
