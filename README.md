================================================================================

TRUVEX AI - AI Against Misinformation & Digital Trust
"Don't just read it. Verify it."

OVERVIEW

TruVex AI is a full-stack, enterprise-grade misinformation detection and digital
trust platform. It empowers users to analyze URLs from social media (Instagram,
WhatsApp, X/Twitter, Facebook, YouTube, Telegram, Reddit, TikTok) and news
websites, or submit pasted text and post screenshots.

The system performs deep platform detection, decomposes complex content into
testable atomic claims, verifies each claim against independent live web evidence
without hallucination, scores source credibility across a curated 600+ domain
database, detects timeline recirculation of old news, maps an interactive source
relationship graph, and generates an explainable trust dashboard.

KEY FEATURES

Multi-Platform Input & Source Detection:

Analyzes URLs from Instagram, WhatsApp, Facebook, X/Twitter, YouTube,
Telegram, Reddit, TikTok, blogs, and news sites.

Gracefully flags restricted/inaccessible content (login walls, private
accounts) with guidance to paste text or upload screenshots.

Text and Screenshot upload fallbacks for private chat forwards.

Claim Extraction Engine:

Isolates factual assertions from headlines and body text while excluding
rhetorical questions and subjective opinions.

Supports both an autonomous local NLP extractor and Gemini 2.5 Flash
synthesis.

Live Search & Fact-Checking Engine:

Searches independent web sources in real time using multi-query targeted
variations (exact claim, named entities, fact-checking prefixes).

Prioritizes government (.gov), academic (.edu), wire agencies (Reuters,
AP, AFP), scientific journals (Nature, Science), and certified fact-checkers
(Snopes, PolitiFact, FactCheck.org).

Evidence links and snippets come from search results; verdicts remain
unverified when evidence is insufficient.

Evidence Comparison & Claim-by-Claim Stance:

Displays supporting and contradicting evidence with direct URLs and source
credibility badges.

Supported verdicts: TRUE, MOSTLY TRUE, MISLEADING, UNVERIFIED,
MOSTLY FALSE, FALSE.

Never forces a binary TRUE/FALSE decision when evidence is inconclusive.

Composite Trust & Accuracy Scoring:

Overall Trust Score (0-100) with animated SVG circular gauge.

Sub-score breakdown:

Claim Accuracy (%)

Source Credibility (%)

Evidence Strength (%)

Manipulation Risk (%)

Mandatory disclaimer: "AI-generated confidence estimate based on
available evidence."

Timeline Recirculation Detection:

Compares event timestamps to detect cases where years-old archival media
is shared as breaking news.

Displays: 

$$!$$

 POSSIBLE OLD NEWS RECIRCULATION when detected.

Interactive Source Relationship Graph:

Visual flow representation:
USER URL -> SOURCE PLATFORM -> ARTICLE/POST -> CLAIMS ->
FACT-CHECK SOURCES -> EVIDENCE -> FINAL VERDICT

Interactive SVG diagram with color-coded nodes and relationship links.

Original Source Discovery & Related News:

Identifies the earliest or primary reporting outlet with evidence rationale.

Surfaces independent related articles covering the event.

Image & Media Forensics:

Analyzes EXIF metadata, camera hardware traces, software editing signatures
(Photoshop, Canva, Midjourney), and compression patterns.

Conservative reporting: "Image authenticity could not be reliably
determined" when inconclusive.

Persistent History & Exporting:

Stores past analyses in an embedded SQLite database (data/truvex.db).

Slide-out history drawer to reload past investigations.

Export reports as JSON, Copy Markdown, or Print/PDF.

PROJECT LAYOUT

truvex-ai/
|-- .venv/                          # Local Python virtual environment
|-- backend/
|   |-- init.py
|   |-- config.py                   # Environment config & constants
|   |-- models.py                   # Pydantic data schemas
|   |-- database.py                 # SQLite persistence layer
|   |-- sample_data.py              # 1-click demo test presets
|   |-- services/
|   |   |-- platform_detector.py    # Regex & domain platform detection
|   |   |-- content_extractor.py    # OpenGraph, Schema.org, oEmbed scraper
|   |   |-- credibility_service.py  # 600+ domain database & satire detector
|   |   |-- claim_extractor.py      # Claim decomposition engine
|   |   |-- search_service.py       # Real-time multi-query search
|   |   |-- verification_service.py # Stance comparison, scores & verdicts
|   |   |-- timeline_service.py     # Old news recirculation checker
|   |   |-- image_forensics.py      # EXIF & compression analysis
|   |   -- graph_service.py        # Node-edge relationship generator |   -- main.py                     # FastAPI application & REST routes
|-- frontend/
|   |-- index.html                  # Cyber-trust themed SPA dashboard
|   |-- styles.css                  # Dashboard styling
|   |-- app.js                      # Dashboard controller & API client
|   |-- graph.js                    # Interactive SVG relationship graph
|   -- history.js                  # History drawer & export utilities |-- run.py                          # Startup launcher script |-- README.txt                      # Project documentation -- requirements.txt                # Python dependencies

INSTALLATION & RUNNING

Prerequisites:

Python 3.11+

Windows, macOS, or Linux

Active internet connection (for live evidence searches)

Windows (PowerShell):
python -m venv .venv
..venv\Scripts\python.exe -m pip install --upgrade pip
..venv\Scripts\python.exe -m pip install -r requirements.txt
..venv\Scripts\python.exe run.py

macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python run.py

Configuration & Environment Variables:

GEMINI_API_KEY (Optional): Set in environment or root .env file.
Without this key, the system defaults to built-in rule-based claim
extraction and verification.

HOST (Optional): Defaults to 127.0.0.1.

PORT (Optional): Defaults to 8000.

RELOAD (Optional): Set to 1 to enable auto-reloading during development.

Dashboard Access:
Open http://127.0.0.1:8000 in your browser.

API DOCUMENTATION

Interactive Swagger UI is accessible at:
http://127.0.0.1:8000/docs

Primary Endpoints:

POST   /api/analyze       Submit URL, text, and/or image for fact-checking

GET    /api/history       Retrieve past verification summaries

GET    /api/history/{id}  Retrieve full report for a specific check

DELETE /api/history/{id}  Delete an analysis entry

DELETE /api/history       Clear all history records

GET    /api/demos         Fetch preset demo scenarios

GET    /api/status        Check engine status and active services
