import os
import sys
import argparse
import uvicorn
from backend.config import SERVER_HOST, SERVER_PORT

def main():
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="TruVex AI - Misinformation & Digital Trust Platform Launcher")
    parser.add_argument("--host", default=SERVER_HOST, help=f"Host address (default: {SERVER_HOST})")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help=f"Port number (default: {SERVER_PORT})")
    parser.add_argument("--reload", action="store_true", default=None, help="Enable auto-reload on code changes")
    args = parser.parse_args()

    reload_env = os.getenv("RELOAD", "").strip().lower() in {"1", "true", "yes", "on"}
    reload_enabled = args.reload if args.reload is not None else reload_env

    print("============================================================")
    print("  TruVex AI - AI Against Misinformation & Digital Trust")
    print(f"  Server starting at: http://{args.host}:{args.port}")
    print(f"  API Docs available at: http://{args.host}:{args.port}/docs")
    print("  Frontend & Backend fully integrated and running!")
    print("============================================================")

    try:
        uvicorn.run(
            "backend.main:app",
            host=args.host,
            port=args.port,
            reload=reload_enabled,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nTruVex AI server shutdown gracefully.")

if __name__ == "__main__":
    main()
