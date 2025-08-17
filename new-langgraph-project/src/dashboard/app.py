import json
import os
import sys
import time
import webbrowser
from pathlib import Path
from typing import List

import streamlit as st


def load_langgraph_config(base: Path) -> dict:
    cfg_path = base / "langgraph.json"
    if not cfg_path.exists():
        return {}
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def env_summary(keys):
    rows = []
    for k in keys:
        val = os.getenv(k)
        masked = None if val is None else (val if len(val) <= 6 else f"{val[:3]}…{val[-3:]}")
        rows.append((k, masked, "set" if val else "missing"))
    return rows


def package_version(name: str) -> str:
    try:
        import importlib.metadata as md  # py3.8+

        return md.version(name)
    except Exception:
        return "not installed"


def main() -> None:
    base = Path(__file__).resolve().parents[2]
    st.set_page_config(page_title="LangGraph Project Dashboard", layout="wide")
    st.title("LangGraph Project Dashboard")
    st.caption("No WSL required. Windows, macOS, Linux supported. Single dashboard + single venv.")

    # Sidebar: section selector
    section = st.sidebar.radio("Section", ["Overview", "Invoke", "Console", "Mem0", "Logs"], index=0)

    # Target project selector (Template vs Sportman)
    st.sidebar.markdown("### Target Project")
    target = st.sidebar.selectbox("Project", ["sportman", "template"], index=0)
    if target == "sportman":
        target_base = base.parents[0] / "sportman"
        default_api_port = 8123
        default_studio_port = 3000
    else:
        target_base = base
        default_api_port = 8124
        default_studio_port = 3001

    host = st.sidebar.text_input("Host", value="127.0.0.1")
    api_port = st.sidebar.number_input("API Port", value=default_api_port, min_value=1, max_value=65535, step=1)
    studio_port = st.sidebar.number_input("Studio Port", value=default_studio_port, min_value=1, max_value=65535, step=1)
    api_url = f"http://{host}:{int(api_port)}"
    studio_url = f"http://{host}:{int(studio_port)}/"

    if section == "Overview":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Environment")
            st.write(f"Python: {sys.version.split()[0]}")
            st.write(f"Working dir: {base}")
            keys = [
                "OPENAI_API_KEY",
                "AZURE_OPENAI_API_KEY",
                "AZURE_OPENAI_API_VERSION",
                "AZURE_OPENAI_ENDPOINT",
                "TAVILY_API_KEY",
                "ODDS_API_KEY",
                "LANGSMITH_API_KEY",
            ]
            rows = env_summary(keys)
            st.table({"Key": [r[0] for r in rows], "Value": [r[1] for r in rows], "Status": [r[2] for r in rows]})

        with col2:
            st.subheader("Packages")
            st.write(
                {
                    "langgraph-cli": package_version("langgraph-cli"),
                    "langgraph-api": package_version("langgraph-api"),
                    "langgraph": package_version("langgraph"),
                    "langsmith": package_version("langsmith"),
                    "openai": package_version("openai"),
                }
            )

        cfg = load_langgraph_config(target_base)
        st.subheader("Graphs (from langgraph.json)")
        graphs = (cfg or {}).get("graphs", {})
        if not graphs:
            st.info("No graphs found. Ensure langgraph.json lists your graphs.")
        else:
            st.json(graphs)

        st.subheader("Quick Actions")
        docs_url = f"{api_url}/docs"
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Open API Docs"):
                webbrowser.open(docs_url)
        with c2:
            if st.button("Open Studio"):
                webbrowser.open(studio_url)
        with c3:
            st.write("Verify target:")
            try:
                import httpx

                r = httpx.get(docs_url, timeout=3.0)
                st.success(f"Docs HTTP {r.status_code}")
            except Exception as e:
                st.warning(f"Docs check failed: {e}")

        st.caption(
            "Use the sidebar to switch between the template and the sportman project."
        )

        st.subheader("Notes")
        st.markdown(
            "- Use PowerShell on Windows; no WSL needed.\n"
            "- Set API keys in .env or your shell.\n"
            "- For tracing, set LANGCHAIN_TRACING_V2=true and LANGSMITH_API_KEY."
        )

    elif section == "Invoke":
        st.subheader("Invoke Graph")
        cfg = load_langgraph_config(target_base)
        graphs = (cfg or {}).get("graphs", {})
        if not graphs:
            st.info("No graphs found in langgraph.json for the selected project.")
            return

        graph_ids = list(graphs.keys())
        graph_id = st.selectbox("Graph", graph_ids, index=0)

        def default_input_for(gid: str) -> str:
            try:
                # Provide helpful defaults for sportman graphs
                if gid == "agent":
                    return "{\n  \"user_input\": \"hello\"\n}"
                if gid == "events":
                    return "{\n  \"sport_key\": \"basketball_nba\",\n  \"region\": \"us\"\n}"
                if gid == "markets":
                    return "{\n  \"sport_key\": \"basketball_nba\",\n  \"event_id\": \"<fill-event-id>\",\n  \"markets\": \"h2h,spreads,totals\",\n  \"region\": \"us\"\n}"
                if gid == "sports_data":
                    return "{\n  \"league_path\": \"basketball/nba/scoreboard\"\n}"
                # mem0 graphs (template)
                if gid == "mem_list" or gid == "mem_dump":
                    return "{}"
                if gid == "mem_add":
                    return "{\n  \"title\": \"Sample\",\n  \"content\": \"Hello from dashboard\",\n  \"tags\": \"demo,notes\"\n}"
            except Exception:
                pass
            return "{}"

        st.caption("Input JSON (sent as 'input')")
        input_text = st.text_area("Input", value=default_input_for(graph_id), height=180)

        with st.expander("Optional: Runtime context (body.context)"):
            ctx_text = st.text_area(
                "Context JSON",
                value="{}",
                height=120,
            )

        with st.expander("Optional: Configurable (body.config.configurable)"):
            conf_text = st.text_area(
                "Configurable JSON",
                value="{}",
                height=120,
            )

        if st.button("Invoke"):
            try:
                import json as _json
                import httpx

                input_obj = _json.loads(input_text or "{}")
                body = {"assistant_id": graph_id, "input": input_obj}

                # Attach optional context
                try:
                    ctx_obj = _json.loads(ctx_text or "{}")
                    if isinstance(ctx_obj, dict) and ctx_obj:
                        body["context"] = ctx_obj
                except Exception:
                    pass

                # Attach optional configurable
                try:
                    conf_obj = _json.loads(conf_text or "{}")
                    if isinstance(conf_obj, dict) and conf_obj:
                        body["config"] = {"configurable": conf_obj}
                except Exception:
                    pass

                url = f"{api_url}/runs/wait"
                with httpx.Client(timeout=30.0) as client:
                    r = client.post(url, json=body)
                    r.raise_for_status()
                    st.success(f"HTTP {r.status_code}")
                    st.subheader("Response")
                    st.code(r.text, language="json")
            except Exception as e:
                st.error(f"Invoke failed: {e}")

    elif section == "Console":
        st.subheader("Codex Console (Windows PowerShell)")
        repo_root = base.parents[0]
        logs_dir = repo_root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        console_log = logs_dir / "codex_console.log"
        registry_path = logs_dir / "process_registry.json"

        # Global process registry (avoid touching session_state inside threads)
        if "_next_job_id" not in st.session_state:
            st.session_state._next_job_id = 1
        # Module-level registry for running processes
        global _CONSOLE_PROCS
        try:
            _CONSOLE_PROCS
        except NameError:
            _CONSOLE_PROCS = {}
        # Module-level registry for named long-running processes (to prevent duplicates)
        global _NAMED_PROCS, _NAMED_JOBS
        try:
            _NAMED_PROCS
        except NameError:
            _NAMED_PROCS = {}
        try:
            _NAMED_JOBS
        except NameError:
            _NAMED_JOBS = {}

        # Persistent registry helpers
        def _read_registry() -> dict:
            try:
                return json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else {}
            except Exception:
                return {}

        def _write_registry(data: dict) -> None:
            try:
                registry_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except Exception:
                pass

        def _update_registry(name: str, info: dict) -> None:
            data = _read_registry()
            data[name] = info
            _write_registry(data)

        def _remove_registry(name: str) -> None:
            data = _read_registry()
            if name in data:
                data.pop(name, None)
                _write_registry(data)

        import threading
        import subprocess
        import datetime as _dt

        def _is_alive(p) -> bool:
            try:
                return p and (p.poll() is None)
            except Exception:
                return False

        def stop_named(name: str) -> None:
            p = _NAMED_PROCS.get(name)
            if _is_alive(p):
                try:
                    p.kill()
                except Exception:
                    pass
            _NAMED_PROCS.pop(name, None)
            _NAMED_JOBS.pop(name, None)
            # Fallback to registry PID stop if needed
            try:
                reg = _read_registry().get(name) or {}
                pid = reg.get("pid")
                if pid:
                    try:
                        subprocess.run(["powershell","-NoProfile","-Command", f"try {{ Stop-Process -Id {int(pid)} -Force }} catch {{}}"], check=False)
                    except Exception:
                        pass
            except Exception:
                pass
            _remove_registry(name)

        def spawn_ps(cmd: str, cwd: str | None = None, name: str | None = None):
            job_id = st.session_state._next_job_id
            st.session_state._next_job_id += 1
            ts = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            header = f"\n===== [{ts}] JOB {job_id} START =====\nCWD: {cwd or repo_root}\nCMD: {cmd}\n"
            console_log.write_text((console_log.read_text(encoding="utf-8") if console_log.exists() else "") + header, encoding="utf-8")

            def _run():
                with open(console_log, "a", encoding="utf-8", newline="") as lf:
                    try:
                        # Ensure singleton per named process
                        if name:
                            stop_named(name)
                        p = subprocess.Popen(
                            ["powershell", "-NoProfile", "-Command", cmd],
                            cwd=cwd or str(repo_root),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            bufsize=1,
                            universal_newlines=True,
                        )
                        _CONSOLE_PROCS[job_id] = p
                        if name:
                            _NAMED_PROCS[name] = p
                            _NAMED_JOBS[name] = job_id
                            _update_registry(name, {
                                "pid": getattr(p, "pid", None),
                                "cmd": cmd,
                                "cwd": cwd or str(repo_root),
                                "started_at": ts,
                            })
                        for line in p.stdout:  # type: ignore[arg-type]
                            lf.write(line)
                        rc = p.wait()
                        lf.write(f"\n[exit {rc}]\n")
                    except Exception as e:  # pragma: no cover
                        lf.write(f"\n[error] {e}\n")
                    finally:
                        lf.write(f"===== JOB {job_id} END =====\n")
                        lf.flush()
                        _CONSOLE_PROCS.pop(job_id, None)
                        if name and _NAMED_JOBS.get(name) == job_id:
                            _NAMED_PROCS.pop(name, None)
                            _NAMED_JOBS.pop(name, None)
                            _remove_registry(name)

            t = threading.Thread(target=_run, daemon=True)
            t.start()
            return job_id

        c1, c2 = st.columns([3, 1])
        with c1:
            cmd = st.text_input("PowerShell command", value="dir")
        with c2:
            workdir = st.text_input("Working dir", value=str(repo_root))

        c3, c4 = st.columns([1, 1])
        with c3:
            st.markdown('<div data-testid="btn-run-command"></div>', unsafe_allow_html=True)
            if st.button("Run Command", key="console-run"):
                if cmd.strip():
                    spawn_ps(cmd.strip(), cwd=workdir.strip() or None)
        with c4:
            if st.button("Stop All Running"):
                for p in list(_CONSOLE_PROCS.values()):
                    try:
                        p.kill()
                    except Exception:
                        pass
                _CONSOLE_PROCS.clear()
                _NAMED_PROCS.clear()
                _NAMED_JOBS.clear()

        st.divider()
        st.caption("Quick: Sportman controls (8123/3000)")
        sc1, sc2, sc3 = st.columns([1,1,1])
        sportman_dir = repo_root / 'sportman'
        template_dir = base
        with sc1:
            st.markdown('<div data-testid="btn-start-sportman"></div>', unsafe_allow_html=True)
            if st.button("Start Sportman Server", key="start-sportman"):
                cmd_sm = ".\\.venv\\Scripts\\langgraph.exe dev --host 127.0.0.1 --port 8123 --debug-port 3000 --no-browser"
                spawn_ps(cmd_sm, cwd=str(sportman_dir), name="sportman")
        with sc2:
            st.markdown('<div data-testid="btn-stop-sportman"></div>', unsafe_allow_html=True)
            if st.button("Stop Sportman Server", key="stop-sportman"):
                # Prefer killing tracked process; fall back to freeing ports
                stop_named("sportman")
                kill_cmd = "Get-NetTCPConnection -State Listen -LocalPort 8123,3000 -ErrorAction SilentlyContinue | Select -Expand OwningProcess -Unique | % { try { Stop-Process -Id $_ -Force } catch {} }"
                spawn_ps(kill_cmd)
        with sc3:
            st.markdown('<div data-testid="btn-stop-template"></div>', unsafe_allow_html=True)
            if st.button("Stop Template Server", key="stop-template"):
                kill_cmd = "Get-NetTCPConnection -State Listen -LocalPort 8124,3001 -ErrorAction SilentlyContinue | Select -Expand OwningProcess -Unique | % { try { Stop-Process -Id $_ -Force } catch {} }"
                spawn_ps(kill_cmd)
        st.markdown('<div data-testid="btn-start-template"></div>', unsafe_allow_html=True)
        if st.button("Start Template Server", key="start-template"):
            cmd_tm = ".\\.venv\\Scripts\\langgraph.exe dev --host 127.0.0.1 --port 8124 --debug-port 3001 --no-browser"
            spawn_ps(cmd_tm, cwd=str(template_dir), name="template")

        fc1, fc2 = st.columns([1,2])
        with fc1:
            st.markdown('<div data-testid="btn-free-ports"></div>', unsafe_allow_html=True)
            if st.button("Free Common Ports", key="free-ports"):
                # Stop tracked named processes first
                for name in list(_NAMED_PROCS.keys()):
                    stop_named(name)
                kill_cmd = "Get-NetTCPConnection -State Listen -LocalPort 8592,8593,8123,8124,3000,3001 -ErrorAction SilentlyContinue | Select -Expand OwningProcess -Unique | % { try { Stop-Process -Id $_ -Force } catch {} }"
                spawn_ps(kill_cmd)

        # Status panel
        st.subheader("Status")
        import socket

        def port_open(host: str, port: int, timeout: float = 0.5) -> bool:
            try:
                with socket.create_connection((host, port), timeout=timeout):
                    return True
            except Exception:
                return False

        cols = st.columns(5)
        statuses = [
            ("Dashboard 8592", port_open("127.0.0.1", 8592)),
            ("Sportman API 8123", port_open("127.0.0.1", 8123)),
            ("Template API 8124", port_open("127.0.0.1", 8124)),
            ("Debugger 3000", port_open("127.0.0.1", 3000)),
            ("Debugger 3001", port_open("127.0.0.1", 3001)),
        ]
        for (label, ok), c in zip(statuses, cols):
            c.metric(label, "UP" if ok else "DOWN")

        st.caption("Tracked processes")
        reg = _read_registry()
        if not reg:
            st.write("None")
        else:
            st.table({
                "name": list(reg.keys()),
                "pid": [reg[k].get("pid") for k in reg.keys()],
                "cwd": [reg[k].get("cwd") for k in reg.keys()],
                "cmd": [reg[k].get("cmd") for k in reg.keys()],
                "started_at": [reg[k].get("started_at") for k in reg.keys()],
            })

    elif section == "Mem0":
        st.subheader("Mem0 (file-backed memory store)")
        try:
            import importlib.metadata as md
            ver = md.version("mem0-mcp")
        except Exception:
            ver = "not installed"
        st.caption(f"Package: mem0-mcp {ver}")

        # Try to import store helpers
        try:
            from mem0_mcp import store as mem0_store  # type: ignore
            mem0_ok = True
        except Exception as e:
            mem0_ok = False
            st.error(f"mem0_mcp not available: {e}. Install D:\\mem0 or pip install mem0-mcp.")

        # Allow setting MEM0_PATH for this session
        import os as _os
        current_path = _os.getenv("MEM0_PATH", "")
        new_path = st.text_input("MEM0_PATH (optional):", value=current_path, placeholder="e.g., H:/langgraph/logs/mem0.json")
        colp1, colp2 = st.columns([1,1])
        with colp1:
            if st.button("Apply Path"):
                if new_path:
                    _os.environ["MEM0_PATH"] = new_path
                    st.success(f"MEM0_PATH set to {new_path}")
                else:
                    if "MEM0_PATH" in _os.environ:
                        _os.environ.pop("MEM0_PATH")
                    st.info("MEM0_PATH cleared; using default mem0.json in cwd")
        with colp2:
            if mem0_ok and st.button("Show Resolved Path"):
                try:
                    st.write(str(mem0_store.MEM_PATH))
                except Exception as e:
                    st.warning(f"Unable to resolve: {e}")

        st.divider()
        if mem0_ok:
            c1, c2, c3 = st.columns([1,1,1])
            with c1:
                if st.button("List Notes"):
                    data = mem0_store.load_mem()
                    titles = [n.get("title", "(untitled)") for n in data.get("notes", [])]
                    if not titles:
                        st.info("No notes yet.")
                    else:
                        st.write({"notes": titles})
            with c2:
                if st.button("Dump JSON"):
                    data = mem0_store.load_mem()
                    st.code(json.dumps(data, indent=2), language="json")
            with c3:
                st.write("")

            st.subheader("Add Note")
            nt1, nt2 = st.columns([1,3])
            with nt1:
                title = st.text_input("Title", value="")
            with nt2:
                content = st.text_area("Content", value="")
            tags = st.text_input("Tags (comma separated)", value="")
            if st.button("Save Note"):
                try:
                    tag_list = [t.strip() for t in (tags or "").split(",") if t.strip()]
                    mem0_store.add_note(title or "(untitled)", content or "", tag_list)
                    st.success("Note saved.")
                except Exception as e:
                    st.error(f"Failed to save: {e}")

        # Show running jobs
        if _CONSOLE_PROCS:
            st.caption("Running jobs:")
            for jid, proc in list(_CONSOLE_PROCS.items()):
                st.write(f"JOB {jid} (PID {getattr(proc, 'pid', '?')}) running…")

        st.divider()
        st.caption("Console Output (auto-refresh)")
        refresh = st.number_input("Refresh (s)", min_value=0, max_value=30, value=2, step=1)
        lines = st.number_input("Tail lines", min_value=100, max_value=10000, value=1000, step=100)
        if refresh > 0:
            st.autorefresh(interval=int(refresh * 1000), key="console-refresh")
        if console_log.exists():
            content = console_log.read_text(encoding="utf-8")
            tail = "\n".join(content.splitlines()[-int(lines):])
            st.text_area("", value=tail, height=600, label_visibility="collapsed")
            # Also render content as an HTML <pre> with a test id for headless Playwright
            try:
                import html as _html
                escaped = _html.escape(tail)
            except Exception:
                escaped = tail
            st.markdown(f"<pre data-testid=\"console-output\">{escaped}</pre>", unsafe_allow_html=True)
            st.markdown('<div data-testid="btn-refresh-now"></div>', unsafe_allow_html=True)
            st.button("Refresh Now", key="console-refresh-now")
        else:
            st.info("No console output yet. Run a command to start logging.")

    else:
        # Logs section (consolidated Output Viewer)
        st.subheader("Logs")

        def find_log_files(root: Path, patterns: List[str] = None, max_files: int = 200) -> List[Path]:
            patterns = patterns or ["*.log"]
            found: List[Path] = []
            for pat in patterns:
                for p in root.rglob(pat):
                    try:
                        if p.is_file():
                            found.append(p)
                    except Exception:
                        continue
                    if len(found) >= max_files:
                        return sorted(found)
            return sorted(found)

        def tail_lines(path: Path, n: int = 500, encoding: str = "utf-8") -> str:
            try:
                with path.open("rb") as f:
                    f.seek(0, os.SEEK_END)
                    size = f.tell()
                    window = 256 * 1024
                    start = max(0, size - window)
                    f.seek(start)
                    data = f.read().decode(encoding, errors="replace")
                lines = data.splitlines()
                return "\n".join(lines[-n:])
            except Exception as e:
                return f"<error reading file: {e}>"

        repo_root = base.parents[0]
        defaults = [
            repo_root / "sportman" / "install_verbose.log",
            repo_root / "sportman" / "server_verbose.log",
        ]
        logs = find_log_files(repo_root)
        options = [str(p) for p in defaults if p.exists()] + [str(p) for p in logs]
        options = sorted(set(options))
        sel = st.selectbox("Choose a log file", options) if options else ""
        manual = st.text_input("Or enter a path", value=str(defaults[0]) if defaults and defaults[0].exists() else "")
        path_str = manual or sel
        try:
            path = Path(path_str)
        except Exception:
            path = None

        colA, colB, colC = st.columns(3)
        with colA:
            lines = st.number_input("Tail lines", min_value=50, max_value=5000, value=500, step=50)
        with colB:
            interval = st.number_input("Refresh (s)", min_value=0, max_value=30, value=2, step=1)
        with colC:
            wrap = st.checkbox("Wrap", value=True)

        if not path or not path.exists():
            st.info("Select an existing .log file or enter a valid path.")
        else:
            if interval > 0:
                st.autorefresh(interval=interval * 1000, key=f"refresh-{path}")
            st.caption(f"{path} • {time.ctime(path.stat().st_mtime)}")
            content = tail_lines(path, n=int(lines))
            st.text_area("Output", value=content, height=600, label_visibility="collapsed", disabled=True)
            if wrap:
                st.markdown("<style>textarea { white-space: pre-wrap !important; }</style>", unsafe_allow_html=True)
            st.download_button("Download file", data=path.read_bytes(), file_name=path.name)


if __name__ == "__main__":
    main()
