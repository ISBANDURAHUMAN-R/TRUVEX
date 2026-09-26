TruVex AI
AI Against Misinformation & Digital Trust

"Don't just read it. Verify it."

TruVex AI is a full-stack misinformation detection and digital trust platform designed to help users investigate suspicious online content.

It analyzes social media URLs, news articles, pasted text, and screenshots, extracts factual claims, searches for independent evidence, evaluates source credibility, detects old-news recirculation, and produces an explainable trust report.

What TruVex AI Does

TruVex AI transforms questionable online content into a structured investigation:

URL / Text / Screenshot
        ↓
Platform Detection
        ↓
Content Extraction
        ↓
Claim Decomposition
        ↓
Live Web Evidence Search
        ↓
Evidence Comparison
        ↓
Source Credibility Analysis
        ↓
Timeline Analysis
        ↓
Trust & Accuracy Scoring
        ↓
Explainable Verification Report

The system is designed to avoid forced conclusions. When available evidence is insufficient, the claim can remain UNVERIFIED.

Key Features
Multi-Platform Analysis

TruVex AI supports content originating from:

Instagram
WhatsApp
X / Twitter
Facebook
YouTube
Telegram
Reddit
TikTok
News websites
Blogs
Other web sources

Restricted or inaccessible pages such as private accounts and login-protected posts are gracefully detected.

Users can instead provide:

Pasted text
Screenshots
Public URLs
Intelligent Claim Extraction

Complex articles and posts are broken into individual factual claims.

The extraction engine:

Identifies factual assertions
Separates multiple claims
Ignores rhetorical questions
Filters subjective opinions
Creates testable verification units
Supports local rule-based extraction
Can use Gemini for advanced synthesis

Example:

Original:
"Scientists discovered a new planet yesterday,
and experts say it may support human life."

↓

Claim 1:
Scientists discovered a new planet.

Claim 2:
Experts say the planet may support human life.

Each claim can then be independently investigated.

Live Evidence Verification

TruVex AI performs real-time web searches using multiple targeted queries.

Search strategies can include:

Exact claim
        ↓
Named entities
        ↓
Event-specific variations
        ↓
Fact-checking queries
        ↓
Independent sources

The system prioritizes sources such as:

Government websites
Academic institutions
Scientific publications
Reuters
Associated Press
AFP
Nature
Science
Established fact-checking organizations

Evidence is displayed with:

Source title
Source URL
Relevant snippet
Credibility information
Supporting or contradicting stance
Claim Verdicts

Each claim receives one of six possible verdicts:

Verdict	Meaning
TRUE	Available reliable evidence strongly supports the claim.
MOSTLY TRUE	The claim is substantially supported, but contains minor inaccuracies, missing context, or qualifications.
MISLEADING	The claim may contain factual elements that are correct, but the overall presentation, framing, or missing context could create a false or inaccurate impression.
UNVERIFIED	Available evidence is insufficient, inconclusive, conflicting, or unavailable to reliably determine the claim's accuracy.
MOSTLY FALSE	The claim contains some accurate elements, but the main assertion is contradicted by the available evidence.
FALSE	Available reliable evidence strongly contradicts the claim or demonstrates that the claim is factually incorrect.
Verdict Principles

TruVex AI does not force a binary TRUE or FALSE decision.

The verification engine considers:

Supporting evidence
Contradicting evidence
Source credibility
Number of independent sources
Agreement between sources
Publication dates
Original reporting
Context surrounding the claim
Potential timeline manipulation
Evidence quality and relevance

When evidence is insufficient or conflicting, the system uses:

UNVERIFIED

rather than generating an unsupported conclusion.

Example
Claim:
"Event X happened on January 15, 2025."

Supporting Evidence:
- Government publication confirms the event.
- Two independent news organizations report the same date.

Contradicting Evidence:
- One social media post claims the event occurred on January 20.

Result:
TRUE

The final verdict is accompanied by the underlying evidence so users can independently review the reasoning rather than relying solely on the generated label.

Trust & Accuracy Scoring

TruVex AI generates an overall Trust Score from 0-100.

The dashboard breaks the score into multiple components:

┌─────────────────────────────┐
│        TRUST SCORE          │
│           82 / 100          │
├─────────────────────────────┤
│ Claim Accuracy       86%    │
│ Source Credibility   91%    │
│ Evidence Strength    78%    │
│ Manipulation Risk    23%    │
└─────────────────────────────┘
Score Components
Claim Accuracy
Source Credibility
Evidence Strength
Manipulation Risk

The dashboard includes an animated SVG trust gauge for visual interpretation.

Disclaimer: AI-generated confidence estimate based on available evidence.

Old News Recirculation Detection

Not every misleading post contains completely fake information.

Sometimes genuine old information is presented as breaking news.

TruVex AI compares:

Original Event Date
        ↓
Original Publication
        ↓
Current Post Date
        ↓
Current Context

When significant timeline inconsistencies are detected, the system can display:

POSSIBLE OLD NEWS RECIRCULATION

This helps identify recycled articles, videos, and images presented without their original context.

Interactive Source Relationship Graph

TruVex AI generates an interactive SVG relationship graph showing how information moves through the investigation.

USER URL
   │
   ▼
SOURCE PLATFORM
   │
   ▼
ARTICLE / POST
   │
   ▼
CLAIMS
   │
   ▼
FACT-CHECK SOURCES
   │
   ▼
EVIDENCE
   │
   ▼
FINAL VERDICT

The graph provides a visual explanation of the relationship between the original content and the evidence used during verification.

Original Source Discovery

TruVex AI attempts to identify the earliest or primary reporting source for an event.

The system can surface:

Original reporting
Independent coverage
Related news articles
Supporting sources
Alternative reporting

The report also provides reasoning for why a source may represent the original reporting.

Source Credibility Analysis

TruVex AI evaluates the credibility of sources using a curated database containing more than 600 domains.

The credibility engine considers factors such as:

Domain identity
Source category
Publication type
Known fact-checking organizations
Government and institutional sources
Satire indicators
Source consistency

The system does not treat every website as equally reliable.

Credibility information is presented alongside evidence so users can inspect the sources behind a verification result.

Image & Media Forensics

TruVex AI includes conservative image-analysis capabilities.

Potential signals include:

EXIF metadata
Camera information
Software editing traces
Compression patterns
Photoshop signatures
Canva signatures
AI-generation indicators such as Midjourney metadata

The system avoids making unsupported authenticity claims.

When evidence is insufficient, it reports:

Image authenticity could not be reliably determined.
Persistent Investigation History

Previous investigations are stored locally using SQLite.

Database:

data/truvex.db

The dashboard includes a slide-out history drawer allowing users to:

View previous investigations
Reload reports
Delete individual records
Clear history
Export & Reporting

Investigation results can be exported or shared as:

JSON
Markdown
Print / PDF

This makes TruVex AI suitable for research, demonstrations, documentation, and digital-literacy workflows.

Project Architecture
truvex-ai/
│
├── .venv/
│
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── database.py
│   ├── sample_data.py
│   │
│   ├── services/
│   │   ├── platform_detector.py
│   │   ├── content_extractor.py
│   │   ├── credibility_service.py
│   │   ├── claim_extractor.py
│   │   ├── search_service.py
│   │   ├── verification_service.py
│   │   ├── timeline_service.py
│   │   ├── image_forensics.py
│   │   └── graph_service.py
│   │
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   ├── graph.js
│   └── history.js
│
├── data/
│   └── truvex.db
│
├── run.py
├── requirements.txt
└── README.md
Technology Stack
Backend
Python
FastAPI
Pydantic
SQLite
REST API
AI & Verification
Rule-based NLP
Gemini API
Multi-query web search
Claim verification
Source credibility analysis
Timeline analysis
Image metadata analysis
Frontend
HTML5
CSS3
JavaScript
SVG
Interactive data visualization
Requirements

Before running TruVex AI, install:

Python 3.11+
Internet connection
Modern web browser

Gemini API access is optional.

Installation
Windows

Open PowerShell inside the project directory:

python -m venv .venv

.\.venv\Scripts\python.exe -m pip install --upgrade pip

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

.\.venv\Scripts\python.exe run.py

Then open:

http://127.0.0.1:8000
Linux / macOS
python3 -m venv .venv

source .venv/bin/activate

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

python run.py

Open:

http://127.0.0.1:8000
Environment Configuration

Create a .env file in the project root if required:

GEMINI_API_KEY=your_api_key_here
HOST=127.0.0.1
PORT=8000
RELOAD=1
Configuration
Variable	Required	Default	Description
GEMINI_API_KEY	No	—	Enables Gemini-powered synthesis
HOST	No	127.0.0.1	Server host
PORT	No	8000	Server port
RELOAD	No	Disabled	Enables development auto-reload

Without a Gemini API key, TruVex AI falls back to its built-in processing logic.

API Documentation

Once the application is running, interactive API documentation is available at:

http://127.0.0.1:8000/docs
Main Endpoints
Analyze Content
POST /api/analyze

Submit:

URL
Text
Image

for verification.

Get History
GET /api/history

Returns previous investigation summaries.

Get Investigation
GET /api/history/{id}

Returns the complete report for a specific investigation.

Delete Investigation
DELETE /api/history/{id}

Deletes a specific investigation.

Clear History
DELETE /api/history

Deletes all stored investigations.

Demo Scenarios
GET /api/demos

Returns preset scenarios for testing the platform.

Engine Status
GET /api/status

Checks the status of the verification engine and active services.

Demo Workflow

A typical investigation looks like:

1. User submits a suspicious URL
             ↓
2. TruVex detects the platform
             ↓
3. Content is extracted
             ↓
4. Claims are identified
             ↓
5. Each claim is searched independently
             ↓
6. Evidence is collected
             ↓
7. Sources are evaluated
             ↓
8. Supporting and contradicting evidence
   is compared
             ↓
9. Timeline is checked
             ↓
10. Trust score is generated
             ↓
11. Source relationship graph is created
             ↓
12. Explainable report is displayed
Verification Philosophy

TruVex AI follows several principles.

Evidence First

Claims should be evaluated against available evidence rather than assumptions.

Independent Verification

A single source should not automatically determine the final result.

Uncertainty Preservation

Insufficient evidence should result in:

UNVERIFIED

rather than an invented conclusion.

Source Awareness

Different sources have different levels of reliability and editorial standards.

Explainability

Users should be able to understand:

What was claimed?
        ↓
What evidence was found?
        ↓
Which sources support it?
        ↓
Which sources contradict it?
        ↓
How was the verdict produced?
Limitations

TruVex AI is an investigative assistance system, not an absolute truth oracle.

Results can be affected by:

Search engine coverage
Newly emerging events
Deleted web pages
Private social media accounts
Login restrictions
Limited evidence
Conflicting sources
Metadata removal
Image recompression
AI-generated content
Rapidly changing information

A high or low score should therefore be interpreted alongside the underlying evidence.

Privacy

TruVex AI is designed to store investigation history locally using SQLite.

Users should avoid submitting:

Passwords
Private credentials
Sensitive personal information
Confidential documents
Private content they are not authorized to process
Project Goals

TruVex AI aims to make digital verification:

Accessible
Explainable
Evidence-driven
Multi-platform
Fast
Trust-focused
Useful for digital literacy

The goal is not simply to answer:

"Is this fake?"

Instead, TruVex AI aims to answer:

"What exactly is being claimed, what evidence exists, where did the information come from, and how strong is that evidence?"

Future Improvements

Potential future development areas include:

Advanced multimodal AI analysis
Video frame verification
Audio and deepfake detection
Browser extension
Mobile application
Multilingual claim extraction
More extensive source credibility datasets
Real-time social-media monitoring
Advanced image provenance detection
Knowledge graph integration
Community-assisted verification
Automated citation generation
Database

Local investigation data is stored in:

data/truvex.db

SQLite keeps the project lightweight while allowing persistent investigation history without requiring an external database server.

Contributing

Contributions are welcome.

Suggested workflow:

git clone <repository-url>

cd truvex-ai

python -m venv .venv

pip install -r requirements.txt

python run.py

Create a feature branch:

git checkout -b feature/new-feature

Commit changes:

git add .
git commit -m "Add new verification feature"

Push the branch:

git push origin feature/new-feature

Then open a Pull Request.

License
completely made by me.


