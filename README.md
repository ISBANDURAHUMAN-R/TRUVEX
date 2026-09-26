# TruVex AI â€“ AI Against Misinformation & Digital Trust

> **"Don't just read it. Verify it."**

TruVex AI is a full-stack, enterprise-grade misinformation detection and digital trust platform. It empowers users to analyze URLs from social media (Instagram, WhatsApp, X/Twitter, Facebook, YouTube, Telegram, Reddit, TikTok) and news websites, or submit pasted text and post screenshots.

The system performs deep platform detection, decomposes complex content into testable atomic claims, verifies each claim against independent live web evidence without hallucination, scores source credibility across a curated 600+ domain database, detects timeline recirculation of old news, maps an interactive source relationship graph, and generates an explainable trust dashboard.

---

## Key Features

1. **Multi-Platform Input & Source Detection**:
   - Analyzes URLs from Instagram, WhatsApp, Facebook, X/Twitter, YouTube, Telegram, Reddit, TikTok, blogs, and news sites.
   - Gracefully flags restricted/inaccessible content (e.g. login walls, private accounts) with clear guidance to paste text or upload screenshots.
   - Text and Screenshot upload fallbacks for private chat forwards (e.g. WhatsApp).

2. **Claim Extraction Engine**:
   - Isolates factual assertions from headlines and body text while excluding rhetorical questions and subjective opinions.
   - Supports both an autonomous local NLP extractor and Gemini 2.5 Flash synthesis.

3. **Live Search & Fact-Checking Engine**:
   - Searches independent web sources in real time using multi-query targeted variations (exact claim, named entities, fact-checking prefixes).
   - Prioritizes government (.gov), academic (.edu), wire agencies (Reuters, AP, AFP), scientific journals (Nature, Science), and certified fact-checkers (Snopes, PolitiFact, FactCheck.org).
   - Evidence links and snippets come from search results; verdicts are estimates and remain unverified when evidence is insufficient.

4. **Evidence Comparison & Claim-by-Claim Stance**:
   - Displays supporting and contradicting evidence for each claim with direct URLs and source credibility badges.
   - Supports verdicts: `TRUE`, `MOSTLY TRUE`, `MISLEADING`, `UNVERIFIED`, `MOSTLY FALSE`, `FALSE`.
   - Never forces a binary TRUE/FALSE decision when evidence is insufficientâ€”assigns `UNVERIFIED`.

5. **Composite Trust & Accuracy Scoring**:
   - Overall Trust Score (0â€“100) with animated SVG circular gauge.
   - Sub-score breakdown:
     - Claim Accuracy (%)
     - Source Credibility (%)
     - Evidence Strength (%)
     - Manipulation Risk (%)
   - Mandatory disclaimer: *"AI-generated confidence estimate based on available evidence."*

6. **Timeline Recirculation Detection**:
   - Compares event timestamps to detect cases where years-old archival media is shared as breaking news.
   - Displays: `âš ï¸ POSSIBLE OLD NEWS RECIRCULATION`.

7. **Interactive Source Relationship Graph**:
   - Visual flow representation: `USER URL` â†’ `SOURCE PLATFORM` â†’ `ARTICLE/POST` â†’ `CLAIMS` â†’ `FACT-CHECK SOURCES` â†’ `EVIDENCE` â†’ `FINAL VERDICT`.
   - Interactive SVG diagram with color-coded nodes and support/contradict relationship links.

8. **Original Source Discovery & Related News**:
   - Identifies the earliest or primary reporting outlet with evidence rationale.
   - Surfaces independent related articles covering the event.

9. **Image & Media Forensics**:
   - Analyzes EXIF metadata, camera hardware traces, software editing signatures (Photoshop, Canva, Midjourney), and compression patterns.
   - Safe and conservative reporting: *"Image authenticity could not be reliably determined."* when inconclusive.

10. **Persistent History & Exporting**:
    - Stores past analyses in an embedded SQLite database (`data/truvex.db`).
    - Slide-out history drawer to reload past investigations.
    - Export reports as JSON, Copy Markdown, or Print/PDF.

---

## Project Layout

```
truvex-ai/
â”œâ”€â”€ .venv/                         # Local Python virtual environment (create during setup)
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ config.py                  # Environment config & constants
â”‚   â”œâ”€â”€ models.py                  # Pydantic data schemas
â”‚   â”œâ”€â”€ database.py                # SQLite persistence layer
â”‚   â”œâ”€â”€ sample_data.py             # 1-click demo test presets
â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ platform_detector.py   # Regex & domain platform detection
â”‚   â”‚   â”œâ”€â”€ content_extractor.py   # OpenGraph, Schema.org, oEmbed scraper
â”‚   â”‚   â”œâ”€â”€ credibility_service.py # 600+ domain database & satire detector
â”‚   â”‚   â”œâ”€â”€ claim_extractor.py     # Claim decomposition engine
â”‚   â”‚   â”œâ”€â”€ search_service.py      # Real-time multi-query search
â”‚   â”‚   â”œâ”€â”€ verification_service.py# Stance comparison, scores & verdicts
â”‚   â”‚   â”œâ”€â”€ timeline_service.py    # Old news recirculation checker
â”‚   â”‚   â”œâ”€â”€ image_forensics.py     # EXIF & compression analysis
â”‚   â”‚   â””â”€â”€ graph_service.py       # Node-edge relationship generator
â”‚   â””â”€â”€ main.py                    # FastAPI application & REST routes
â”œâ”€â”€ frontend/
â”‚   â”œâ”€â”€ index.html                 # Cyber-trust themed SPA dashboard
â”‚   â”œâ”€â”€ styles.css                 # Dashboard styling
â”‚   â”œâ”€â”€ app.js                     # Dashboard controller & API client
â”‚   â”œâ”€â”€ graph.js                   # Interactive SVG relationship graph
â”‚   â””â”€â”€ history.js                 # History drawer & export utilities
â”œâ”€â”€ run.py                         # Startup launcher script
â””â”€â”€ README.md                      # Documentation
```

---

## Installation & Running

### Prerequisites
- Python 3.11+
- Windows, macOS, or Linux

Create a virtual environment and install the dependencies from the project directory.

**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python run.py
```

The Gemini integration is optional. To enable it, set `GEMINI_API_KEY` in the environment or add it to a project-root `.env` file. Without a key, the app uses its built-in rule-based claim extraction and verification.

Open the dashboard at:
   ```
   http://127.0.0.1:8000
   ```

The server binds to `127.0.0.1:8000` by default. Set `HOST` or `PORT` before starting to change those values. Live evidence search requires an internet connection.

Automatic reload is off by default. Set `RELOAD=1` before running `run.py` to enable it during development.

---

## API Documentation

The REST API is documented interactively via Swagger UI at:
`http://127.0.0.1:8000/docs`

### Key Endpoints:
- `POST /api/analyze`: Submit URL, text, and/or image for full fact-checking.
- `GET /api/history`: Retrieve past verification history summaries.
- `GET /api/history/{id}`: Retrieve detailed saved analysis report.
- `DELETE /api/history/{id}`: Delete an analysis report.
- `DELETE /api/history`: Clear all history.
- `GET /api/demos`: Fetch preset demo cases.
- `GET /api/status`: Check engine status and active services.


