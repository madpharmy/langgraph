import pytest


DOC_PAGES = [
    # LangGraph docs pages likely to be stable
    ("https://langchain-ai.github.io/langgraph/", "LangGraph"),
    ("https://langchain-ai.github.io/langgraph/concepts/langgraph_cli/", "LangGraph CLI"),
    (
        "https://langchain-ai.github.io/langgraph/tutorials/langgraph-platform/local-server/",
        "Local Server",
    ),
    ("https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/", "LangGraph Studio"),
]


@pytest.mark.e2e
@pytest.mark.parametrize("url,needle", DOC_PAGES)
def test_docs_pages_load(page, url: str, needle: str):
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    # Basic assertions: title contains keyword or an H1 exists
    title = page.title()
    body_text = page.locator("body").inner_text(timeout=30000)
    assert needle.lower() in (title + " " + body_text).lower()
    # Footer often has an edit link; tolerate absence
    edits = page.get_by_text("Edit", exact=False)
    if edits.count() > 0:
        assert edits.first.is_visible()
