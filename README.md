<div align="center">

# 🛡️ TruVex AI

### AI Against Misinformation & Digital Trust

[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Status](https://img.shields.io/badge/Status-Live%20%26%20Active-brightgreen)](http://127.0.0.1:8000)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Repo](https://img.shields.io/badge/GitHub-ISBANDURAHUMAN--R%2FTRUVEX-181717?logo=github)](https://github.com/ISBANDURAHUMAN-R/TRUVEX)

> **"Don't just read it. Verify it."**

A full-stack, enterprise-grade fact-checking and digital trust intelligence platform. Decomposes viral posts, social media claims, and breaking headlines into testable assertions, cross-examines independent authoritative evidence in real time, scores source credibility, flags old recirculated footage, and renders an explainable trust dashboard.

[Explore Features](#-key-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture--pipeline) • [API Reference](#-api-reference)

</div>

---

## ⚡ Key Features

- **🌐 Multi-Platform Input & Source Detection**
  - Automatically identifies and extracts content from **Instagram, WhatsApp, X/Twitter, Facebook, YouTube, Telegram, Reddit, TikTok**, and independent news outlets.
  - Gracefully handles login-walled or private content by offering instantaneous pasted-text and screenshot fallbacks.

- **🧩 Autonomous Claim Decomposition**
  - Breaks down complex, sensationalized articles or message forwards into distinct, testable factual assertions.
  - Filters out subjective opinions, rhetorical questions, and emotional hyperbole.

- **🔍 Multi-Query Real-Time Evidence Gathering**
  - Executes live searches across authoritative sources (wire agencies like Reuters, AP, AFP; scientific journals like Nature, Science; government databases `.gov`, `.edu`; and verified fact-checkers like Snopes, PolitiFact).
  - **Strict Anti-Hallucination Policy:** Every single citation is retrieved live from the web—never invented.

- **⚖️ Evidence Comparison & Verdict Stance**
  - Generates clear supporting and contradicting evidence cards for each claim with direct source links.
  - Verdict spectrum: `🟢 TRUE`, `🟡 MOSTLY TRUE`, `🟠 MISLEADING`, `🔴 MOSTLY FALSE`, `🔴 FALSE`, or `⚪ UNVERIFIED`.

- **📊 Composite Digital Trust Score (0–100)**
  - Dynamic Trust Meter with sub-metric breakdown:
    - **Claim Accuracy (%)**
    - **Source Credibility (%)**
    - **Evidence Strength (%)**
    - **Manipulation Risk (%)**

- **⏳ Timeline Recirculation Detection**
  - Cross-references event timestamps to flag archival media or years-old crises masquerading as today's breaking news (`⚠️ POSSIBLE OLD NEWS RECIRCULATION`).

- **🕸️ Interactive Source Relationship Graph**
  - Visual node-edge flow tracing the path from user submission to platform, claims, authoritative sources, and final verdict.

- **🖼️ Image & Metadata Forensics**
  - Inspects EXIF metadata, camera hardware profiles, compression artifacts, and software manipulation signatures (Photoshop, Midjourney, Canva).

- **📂 Persistent History & Exporting**
  - Embedded local SQLite database (`data/truvex.db`) stores investigation history.
  - Export reports as formatted **JSON**, copy **Markdown**, or **Print/PDF**.

---

## 🏗️ Architecture & Pipeline

```text
[ USER INPUT ] (URL / Text / Screenshot)
       │
       ▼
[ Platform & Content Extractor ] ──► (Metadata, OpenGraph, Canonical Body)
       │
       ▼
[ Claim Extraction Engine ] ───────► (Decomposes into Atomic Testable Claims)
       │
       ▼
[ Live Multi-Query Search ] ───────► (Reuters, AP, .gov, .edu, Fact-Checkers)
       │
       ▼
[ Evidence & Stance Verification ] ─► (Supports / Contradicts / Unverified)
       │
       ▼
[ Credibility & Timeline Check ] ──► (600+ Domain Registry & Recirculation Scan)
       │
       ▼
[ Composite Trust Scoring ] ───────► (Accuracy, Credibility, Evidence, Risk)
       │
       ▼
[ Unified Web Dashboard ] ─────────► (Gauge, Graph, Evidence Cards, History)
```

---

## 📁 Repository Structure

```text
TRUVEX/
├── backend/
│   ├── __init__.py                  # Backend module definition
│   ├── config.py                    # Environment settings, constants & paths
│   ├── database.py                  # SQLite history persistence layer
│   ├── main.py                      # FastAPI application & REST endpoints
│   ├── models.py                    # Pydantic schemas & response models
│   ├── sample_data.py               # 1-click test scenario presets
│   └── services/
│       ├── claim_extractor.py       # Atomic claim isolation engine
│       ├── content_extractor.py     # Web scraper & metadata extractor
│       ├── credibility_service.py   # 600+ domain reputation & satire detector
│       ├── graph_service.py         # Visual node-edge relationship generator
│       ├── image_forensics.py       # EXIF & image compression analyzer
│       ├── platform_detector.py     # URL & social network detector
│       ├── search_service.py        # Real-time multi-query search client
│       ├── timeline_service.py      # Old news recirculation checker
│       └── verification_service.py  # Fact verification & scoring engine
├── frontend/
│   ├── index.html                   # Single-Page Application dashboard
│   ├── styles.css                   # Cyber-trust glassmorphism stylesheet
│   ├── app.js                       # Frontend controller & API client
│   ├── graph.js                     # SVG interactive relationship graph
│   └── history.js                   # History drawer & report exporters
├── tests/
│   ├── test_misinformation.py       # Detection accuracy unit tests
│   └── test_truvex.py               # Comprehensive end-to-end verification suite
├── data/
│   └── .gitkeep                     # Preserves data directory structure
├── requirements.txt                 # Python dependencies
├── run.py                           # Python server launcher
├── run.bat                          # Windows one-click batch launcher
├── .gitignore                       # Security & cache exclusion rules
└── README.md                        # Project documentation
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11, 3.12, 3.13, or 3.14
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/ISBANDURAHUMAN-R/TRUVEX.git
cd TRUVEX
```

### 2. Set Up Virtual Environment & Dependencies

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Launch the Application

**Option A (Windows 1-Click Launcher):**
```powershell
.\run.bat
```

**Option B (Python directly):**
```bash
python run.py
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## ⚙️ Configuration & Environment

TruVex AI works **100% autonomously out of the box** using built-in NLP heuristics, local credibility databases, and real-time live search.

To optionally enable Google Gemini enhanced synthesis:
1. Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   HOST=127.0.0.1
   PORT=8000
   RELOAD=0
   ```
2. Or input your API key directly via the in-app **⚙️ API Settings** modal (stored locally in browser storage).

---

## 📡 API Reference

When the server is running, interactive Swagger documentation is available at:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/analyze` | Core fact-checking pipeline (URL, text, and/or image) |
| `GET` | `/api/status` | Engine capability & health report |
| `GET` | `/api/health` | Simple liveness health check |
| `GET` | `/api/demos` | Preset 1-click test scenarios |
| `GET` | `/api/history` | List past analysis summaries (up to 50) |
| `GET` | `/api/history/{id}` | Retrieve full report of a specific analysis |
| `DELETE`| `/api/history/{id}` | Delete a specific analysis record |
| `DELETE`| `/api/history` | Clear all saved history |

---

## 🧪 Running Tests

Verify the full fact-checking and scoring pipeline using `pytest`:

```powershell
.\.venv\Scripts\python.exe -m pytest tests
```

---

## 🛡️ License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

<div align="center">
Developed with ❤️ by <a href="https://github.com/ISBANDURAHUMAN-R">ISBANDURAHUMAN-R</a>
</div>
