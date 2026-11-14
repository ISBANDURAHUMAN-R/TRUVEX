import os
from pathlib import Path
from dotenv import load_dotenv

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "truvex.db"

# Load project-local settings when present; environment variables still take precedence.
load_dotenv(BASE_DIR / ".env")

# API & Environment Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
SERVER_HOST = os.getenv("HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("PORT", "8000"))

# Search and verification settings
MAX_SEARCH_RESULTS_PER_CLAIM = 5
MAX_CLAIMS_PER_ANALYSIS = 4
REQUEST_TIMEOUT = 12.0
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 (TruVex AI Research Bot)"
