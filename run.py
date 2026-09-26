import os
import sys
import uvicorn
from backend.config import SERVER_HOST, SERVER_PORT

if __name__ == "__main__":
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print("============================================================")
    print("  TruVex AI - AI Against Misinformation & Digital Trust")
    print(f"  Server starting at: http://{SERVER_HOST}:{SERVER_PORT}")
    print("  Frontend & Backend fully integrated and running!")
    print("============================================================")
    reload_enabled = os.getenv("RELOAD", "").strip().lower() in {"1", "true", "yes", "on"}
    uvicorn.run("backend.main:app", host=SERVER_HOST, port=SERVER_PORT, reload=reload_enabled)
