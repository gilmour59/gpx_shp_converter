from __future__ import annotations

import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

from streamlit.web import cli as stcli


HOST = "127.0.0.1"
PORT = 8501
URL = f"http://{HOST}:{PORT}"


def resource_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def _open_browser_when_ready() -> None:
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            with socket.create_connection((HOST, PORT), timeout=1):
                webbrowser.open(URL)
                return
        except OSError:
            time.sleep(0.5)


def main() -> None:
    app_path = resource_path("app.py")

    threading.Thread(
        target=_open_browser_when_ready,
        daemon=True,
    ).start()

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.headless=true",
        f"--server.address={HOST}",
        f"--server.port={PORT}",
        "--browser.gatherUsageStats=false",
    ]
    raise SystemExit(stcli.main())


if __name__ == "__main__":
    main()
