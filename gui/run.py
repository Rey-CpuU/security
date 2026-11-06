#!/usr/bin/env python3
"""
CLI Launcher for the 8-Bit Cyber Operations Office GUI.
Starts the secure localhost FastAPI server and opens the browser.
"""

import argparse
import os
import shutil
import sys
import threading
import time
import webbrowser

# Add repo root to sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

try:
    import uvicorn
except ImportError:
    sys.stderr.write("Error: 'uvicorn' is required. Run 'pip install -r gui/requirements.txt'\n")
    sys.exit(1)


BANNER = r"""
======================================================================
  ______   _____   _______    ____  ______ ______ _____ _____ ______ 
 |  ____| |  __ \ |__   __|  / __ \|  ____|  ____|_   _/ ____|  ____|
 | |__    | |__) |   | |    | |  | | |__  | |__    | || |    | |__   
 |  __|   |  _  /    | |    | |  | |  __| |  __|   | || |    |  __|  
 | |____  | | \ \    | |    | |__| | |    | |     _| || |____| |____ 
 |______| |_|  \_\   |_|     \____/|_|    |_|    |_____\_____|______|
                                                                     
         [ 8-BIT CYBER OPERATIONS OFFICE GUI - v1.0.0 (MVP) ]
======================================================================
"""


def setup_env():
    """Ensure .env exists by copying .env.example if missing."""
    gui_dir = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(gui_dir, ".env")
    env_example = os.path.join(gui_dir, ".env.example")

    if not os.path.isfile(env_file) and os.path.isfile(env_example):
        try:
            shutil.copy(env_example, env_file)
            print("[*] Created default gui/.env from .env.example")
        except Exception:
            pass

    if DOTENV_AVAILABLE and os.path.isfile(env_file):
        load_dotenv(env_file)


def open_browser_delayed(url: str, delay: float = 1.2):
    """Wait for server startup then launch browser."""
    def _open():
        time.sleep(delay)
        print(f"[*] Opening browser to {url} ...")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"[!] Could not open browser automatically: {e}")

    thread = threading.Thread(target=_open, daemon=True)
    thread.start()


def main():
    parser = argparse.ArgumentParser(
        description="Run the 8-Bit Cyber Operations Office GUI."
    )
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"), help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8888")), help="Port to bind (default: 8888)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser on launch")
    args = parser.parse_args()

    setup_env()

    # Enforce local binding safety
    if args.host not in ("127.0.0.1", "localhost"):
        print("[!] Warning: Binding to non-localhost address is dangerous. Forcing 127.0.0.1 for security.")
        args.host = "127.0.0.1"

    os.environ["PORT"] = str(args.port)
    os.environ["HOST"] = str(args.host)

    print(BANNER)
    server_url = f"http://{args.host}:{args.port}"
    print(f"[+] Security Gate    : Active (Localhost + Cryptographic Session Token + Anti-CSWSH)")
    print(f"[+] Office Server    : {server_url}")
    print(f"[+] Active Agents    : 3 MVP Workstations (Rex/Pentest, Ada/AppSec, Gears/DevSecOps)")
    print(f"[+] Concurrency Limit: Max 2 Parallel Workers (FIFO Task Queue)")
    print(f"[+] Press Ctrl+C to terminate the office server.\n")

    if not args.no_browser:
        open_browser_delayed(server_url)

    uvicorn.run(
        "gui.server.app:app",
        host=args.host,
        port=args.port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
