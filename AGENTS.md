# Agent Operating Guidelines (Windows-First, No WSL)

This repository is operated from native Windows PowerShell. Do not use WSL unless it is absolutely necessary to complete a task that cannot be performed natively on Windows.

- No WSL by default: If the terminal path shows `/mnt/...` you are in WSL — switch to Windows PowerShell before proceeding. Prefer `.cmd` wrappers which set `-ExecutionPolicy Bypass` automatically.
- Use provided scripts: See `start_all_windows.cmd`, `scripts\view_logs_windows.cmd`, `new-langgraph-project\scripts\*.cmd` for one-shot starts. Default ports avoid conflicts (8591/8592/8124/3001).
- Do not recommend or rely on "Codex" CLI: Unless explicitly requested by the user, do not suggest or integrate the `@openai/codex` CLI. Prefer standard LangGraph/LangChain patterns and first‑party SDKs (e.g., OpenAI, Azure OpenAI) configured via `.env`.
- Visibility & logs: For long/verbose operations, write output to `.log` files and view via the Output Viewer (Streamlit) on the assigned port. Avoid relying on terminals that truncate output.
- Documentation & tests: Keep guidance Windows‑native. When adding tests or e2e checks, ensure they run without WSL. Use Playwright for external doc/site availability checks.
  - For UI/API changes (dashboard, server routes), add/execute Playwright E2E checks. Prefer Windows PowerShell scripts and built‑in venvs. See examples below.
- Ports: Sportman keeps 8123/3000. Template uses 8124/3001 (API/Debugger) and Streamlit defaults to 8591/8592. Change with `-Port` flags if necessary.

Only deviate from these rules with explicit user approval.

## Playwright E2E (Windows‑Native)

- Template dashboard (Streamlit):
  - Start via `start_all_windows.cmd` (dashboard on `8592`).
  - Run E2E check of the Console tab (invokes a PowerShell command and verifies output):
    - `new-langgraph-project\scripts\test_dashboard_windows.ps1 -DashboardUrl http://127.0.0.1:8592`

- Sportman API (FastAPI):
  - Start via `sportman\scripts\dev_windows.ps1` (API `8123`, debugger `3000`).
  - Docs page check: `SPORTMAN_BASE_URL=http://127.0.0.1:8123` then run `pytest -q tests\e2e\test_docs_page.py::test_docs_page_loads` in `sportman\.venv`.
  - Debugger page check (optional): set `SPORTMAN_DEBUGGER_URL=http://127.0.0.1:3000` and run `tests\e2e\test_debugger_page.py::test_debugger_page_loads`. If debugger UI isn’t running, test skips.

Notes:
- Avoid relying on Codex CLI in tests unless explicitly requested. If the swagger “invoke” E2E uses Codex provider by default, override with `SPORTMAN_USE_CODEX=0` and provide necessary API keys, or skip.
- Keep all runs in native Windows PowerShell. Do not use WSL.
