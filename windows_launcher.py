from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

from streamlit.web import cli as stcli


HOST = "127.0.0.1"
START_PORT = 8501
END_PORT = 8599


def resource_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def find_available_port() -> int:
    requested_port = os.getenv("GPX_SHP_PORT", "").strip()
    if requested_port:
        port = int(requested_port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((HOST, port))
            except OSError as exc:
                raise RuntimeError(
                    f"Requested local port {port} is already in use."
                ) from exc
        return port

    for port in range(START_PORT, END_PORT + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((HOST, port))
                return port
            except OSError:
                continue

    raise RuntimeError(
        f"No available local port found between {START_PORT} and {END_PORT}."
    )


def open_browser_when_ready(port: int) -> None:
    url = f"http://{HOST}:{port}"
    deadline = time.time() + 30

    while time.time() < deadline:
        try:
            with socket.create_connection((HOST, port), timeout=1):
                webbrowser.open(url)
                return
        except OSError:
            time.sleep(0.5)


def validate_packaged_runtime() -> None:
    app_root = resource_path(".")
    app_root_str = str(app_root)
    if app_root_str not in sys.path:
        sys.path.insert(0, app_root_str)

    # Streamlit executes app.py dynamically, so PyInstaller cannot infer all
    # imports from it. Import the application dependency graph explicitly so
    # missing frozen modules fail immediately and are caught by CI.
    import gpxpy  # noqa: F401
    import pandas  # noqa: F401
    import geopandas  # noqa: F401
    import shapely  # noqa: F401
    import pyogrio  # noqa: F401
    import pyproj  # noqa: F401

    from src import converter  # noqa: F401
    from src import csv_attributes  # noqa: F401
    from src import exporter  # noqa: F401
    from src import gpx_parser  # noqa: F401


def main() -> None:
    validate_packaged_runtime()

    app_path = resource_path("app.py")
    port = find_available_port()

    if os.getenv("GPX_SHP_NO_BROWSER") != "1":
        threading.Thread(
            target=open_browser_when_ready,
            args=(port,),
            daemon=True,
        ).start()

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--global.developmentMode=false",
        "--server.headless=true",
        f"--server.address={HOST}",
        f"--server.port={port}",
        "--browser.gatherUsageStats=false",
    ]
    raise SystemExit(stcli.main())


if __name__ == "__main__":
    main()
