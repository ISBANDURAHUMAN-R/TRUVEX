<p align="center">
  <img src="assets/banner.png" alt="TRUVEX Banner" width="100%">
</p>

# ◈ TRUVEX — Multimodal Misinformation Detection Platform

[![TruVex AI CI](https://github.com/ISBANDURAHUMAN-R/TRUVEX/actions/workflows/ci.yml/badge.svg)](https://github.com/ISBANDURAHUMAN-R/TRUVEX/actions)

## ◆ About the Project
TRUVEX is an AI-powered misinformation detection and claims verification system. It decomposes textual and multimodal assertions into testable factual claims, cross-examines independent authoritative evidence, and computes objective credibility and veracity ratings in real time.

```mermaid
flowchart TD
    Input["Input: Text / Article URL / Claim Assertion"] --> CE["Claim Extractor & Entity Parser"]
    CE --> MSR["Multi-Source Evidence Retrieval Engine"]
    MSR -->|"Authoritative Cross-Examination"| VS["Veracity Scorer & Contradiction Analyzer"]
    MSR -->|"Domain Trust & Reputation Database"| CS["Credibility Scoring Engine"]
    VS --> GS["Graph Service (NetworkX Claim Topology)"]
    CS --> GS
    GS --> API["FastAPI REST Endpoints (OpenAPI / Swagger)"]
    API --> UI["React & Tailwind Intelligence Dashboard"]
```

## ❖ Key Features
- Automated claim extraction and decomposition into atomic assertions.
- Multi-source evidence cross-examination and fact-checking retrieval engine.
- Objective veracity scoring algorithm and misinformation risk classification.
- Interactive React and Tailwind CSS intelligence dashboard with claim graph visualizations.
- Modular FastAPI REST API backend with automated OpenAPI / Swagger documentation.
- Comprehensive automated test suite powered by pytest.

## ⬢ Technologies Used
- Python 3.11+
- FastAPI & Pydantic
- NetworkX & NumPy
- Docker & Docker Compose
- React 18 & TypeScript
- Tailwind CSS
- pytest

## § Requirements
- Python 3.11 or higher
- Node.js 18 or higher (for frontend)
- Docker (optional for containerized deployment)

## ▲ Installation & Execution
```bash
# 1. Setup Backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py

# 2. Run Test Suite
pytest tests
```

## ※ Developer
Developer: ISBANDU RAHUMAN R  
GitHub: https://github.com/ISBANDURAHUMAN-R
