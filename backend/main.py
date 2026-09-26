import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response

from backend.config import FRONTEND_DIR, GEMINI_API_KEY
from backend.models import (
    AnalyzeRequest, AnalysisResult, HistorySummary,
    TimelineCheck, ImageAnalysisResult, SourceGraph
)
from backend.database import (
    init_db, save_analysis, get_history, get_analysis_by_id,
    delete_analysis, clear_all_history
)
from backend.services.platform_detector import detect_platform
from backend.services.content_extractor import extract_content_from_url
from backend.services.credibility_service import evaluate_source_credibility
from backend.services.claim_extractor import extract_claims_ai, extract_claims_rule_based
from backend.services.search_service import search_evidence_for_claim, search_available
from backend.services.timeline_service import check_timeline_recirculation
from backend.services.image_forensics import analyze_base64_image, image_forensics_available
from backend.services.graph_service import generate_source_graph
from backend.services.verification_service import (
    verify_single_claim_rule_based, verify_claim_with_gemini,
    calculate_overall_scores, classify_misinformation_type,
    discover_original_source, extract_related_news
)
from backend.sample_data import PRESET_DEMO_CASES

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database
    init_db()
    yield

app = FastAPI(
    title="TruVex AI – AI Against Misinformation & Digital Trust",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/favicon.ico")
async def favicon():
    return Response(content=b"", media_type="image/x-icon")

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "TruVex AI"}

@app.get("/api/status")
async def get_system_status():
    """System health check and engine capability report."""
    now = datetime.now()
    return {
        "status": "online",
        "service": "TruVex AI Engine",
        "timestamp": now.isoformat(),
        "has_gemini_key": bool(GEMINI_API_KEY),
        "search_engine": (
            "DuckDuckGo Live Multi-Query Search (Active)"
            if search_available()
            else "Unavailable; install requirements.txt to enable live search"
        ),
        "search_available": search_available(),
        "image_forensics_available": image_forensics_available(),
        "anti_hallucination_mode": "Search-result URLs with evidence-based estimates",
        "version": "1.0.0"
    }

@app.get("/api/demos")
async def get_demo_cases():
    """Returns preset fact-checking demo cases for rapid testing."""
    return PRESET_DEMO_CASES

@app.get("/api/history", response_model=List[HistorySummary])
async def list_analysis_history(limit: int = 50):
    """Lists previously analyzed URLs and texts."""
    return get_history(limit)

@app.get("/api/history/{analysis_id}")
async def get_single_history(analysis_id: str):
    """Retrieves full details of a saved analysis."""
    record = get_analysis_by_id(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    return record

@app.delete("/api/history/{analysis_id}")
async def delete_single_history(analysis_id: str):
    """Deletes an analysis record."""
    success = delete_analysis(analysis_id)
    if not success:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    return {"message": "Record deleted successfully"}

@app.delete("/api/history")
async def clear_history():
    """Clears all analysis history."""
    clear_all_history()
    return {"message": "All history records cleared successfully"}

@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_content(req: AnalyzeRequest):
    """
    Core AI Fact-Checking Pipeline:
    Platform Detection -> Extraction -> Claims -> Live Search -> Evidence Comparison ->
    Credibility & Timeline Check -> Trust Score -> Verdict -> Graph -> Persistence
    """
    user_url = (req.url or "").strip()
    user_text = (req.text or "").strip()
    image_base64 = req.image_base64
    api_key = req.api_key or GEMINI_API_KEY
    now_dt = datetime.now()
    analysis_id = str(uuid.uuid4())

    if not user_url and not user_text and not image_base64:
        raise HTTPException(status_code=400, detail="Please provide a URL, paste the news text, or upload an image.")

    # 1. Platform Detection
    platform_info = detect_platform(user_url if user_url else None, user_text)

    # 2. Content Extraction
    extracted = {
        "title": "Direct Text Submission",
        "text": user_text,
        "description": "",
        "author": None,
        "publication_date": None,
        "image_url": None,
        "video_url": None,
        "has_citations": False,
        "is_inaccessible": False,
        "inaccessible_message": None
    }

    if user_url:
        extracted = await extract_content_from_url(user_url)
        # If the user also provided text, prioritize user provided text if page was inaccessible
        if user_text:
            extracted["text"] = user_text + ("\n\n" + extracted.get("text", "") if extracted.get("text") else "")
            if not extracted.get("title") or extracted["title"] == "Untitled Web Article":
                extracted["title"] = user_text[:70] + "..."

    # Handle inaccessible platform without user text fallback
    if extracted.get("is_inaccessible") and not user_text and not image_base64:
        cred_eval = evaluate_source_credibility(url=user_url, domain=platform_info["domain"])
        # Return graceful inaccessible status
        empty_graph = SourceGraph(nodes=[], edges=[])
        return AnalysisResult(
            id=analysis_id,
            url=user_url,
            input_text=None,
            platform=platform_info["platform"],
            domain=platform_info["domain"],
            source_type=platform_info["source_type"],
            title=extracted.get("title") or f"Content from {platform_info['platform']}",
            extracted_content=extracted,
            overall_verdict="⚪ UNVERIFIED",
            verdict_badge="UNVERIFIED",
            trust_score=50,
            confidence=0,
            source_credibility=cred_eval["score"],
            source_credibility_explanation=cred_eval["explanation"],
            claim_accuracy=50,
            evidence_strength=0,
            manipulation_risk=50,
            verdict_explanation=(
                f"TruVex AI could not retrieve content directly from {platform_info['platform']} "
                f"due to authentication, private account, or anti-scraping restrictions. "
                "Please copy and paste the post text or upload a screenshot to continue fact-checking."
            ),
            misinformation_type="Unverified claim",
            misinformation_type_explanation="Content could not be accessed directly for analysis.",
            claims=[],
            timeline_check=TimelineCheck(),
            original_source=None,
            related_sources=[],
            image_analysis=None,
            source_graph=empty_graph,
            analysis_timestamp=now_dt.isoformat(),
            last_checked=now_dt.strftime("%B %d, %Y at %I:%M %p"),
            is_inaccessible_platform=True,
            inaccessible_message=extracted.get("inaccessible_message")
        )

    # 3. Image Forensics (if provided)
    image_result = None
    if image_base64:
        image_result_dict = analyze_base64_image(image_base64)
        if image_result_dict:
            image_result = ImageAnalysisResult(
                status=image_result_dict["status"],
                manipulation_risk=image_result_dict["manipulation_risk"],
                exif_details=image_result_dict.get("exif_details", {}),
                forensic_notes=image_result_dict.get("forensic_notes", "")
            )

    # 4. Claim Extraction
    headline_for_claims = extracted.get("title") or (user_text[:80] if user_text else "Submitted Media")
    content_for_claims = extracted.get("text") or extracted.get("description") or user_text
    
    raw_claims = await extract_claims_ai(headline_for_claims, content_for_claims, api_key=api_key, max_claims=3)
    if not raw_claims:
        raw_claims = extract_claims_rule_based(headline_for_claims, content_for_claims, max_claims=3)

    # 5. Live Search & Evidence Gathering per Claim
    all_search_results = []
    verified_claims = []

    for c_text in raw_claims:
        # Search live web evidence using multi-query strategy
        evidence_list = await search_evidence_for_claim(c_text, max_sources=5)
        all_search_results.extend(evidence_list)
        
        # Verify claim against real evidence
        if api_key:
            claim_verif = await verify_claim_with_gemini(c_text, evidence_list, api_key)
        else:
            claim_verif = verify_single_claim_rule_based(c_text, evidence_list)
            
        verified_claims.append(claim_verif)

    # 6. Source Credibility Evaluation
    cred_eval = evaluate_source_credibility(
        url=user_url,
        domain=platform_info["domain"],
        has_author=bool(extracted.get("author")),
        has_citations=extracted.get("has_citations", False)
    )

    # 7. Timeline & Recirculation Check
    timeline = check_timeline_recirculation(
        text=content_for_claims,
        publication_date_str=extracted.get("publication_date"),
        evidence_snippets=all_search_results
    )
    timeline_obj = TimelineCheck(
        original_event_date=timeline["original_event_date"],
        current_post_date=timeline["current_post_date"],
        is_old_recirculated=timeline["is_old_recirculated"],
        warning_message=timeline["warning_message"]
    )

    # 8. Calculate Overall Trust Score & Verdict Banner
    scores = calculate_overall_scores(
        claims_verified=verified_claims,
        source_credibility=cred_eval["score"],
        is_old_recirculated=timeline["is_old_recirculated"]
    )

    # 9. Misinformation Type Classification
    misinfo_type, misinfo_type_expl = classify_misinformation_type(
        verdict_badge=scores["verdict_badge"],
        is_old_recirculated=timeline["is_old_recirculated"],
        claims_verified=verified_claims,
        source_rating=cred_eval["rating"]
    )

    # 10. Original Source Discovery & Related News
    original_source = discover_original_source(all_search_results)
    related_sources = extract_related_news(all_search_results, max_items=4)

    # 11. Visual Relationship Source Graph
    graph_data = generate_source_graph(
        url=user_url,
        platform=platform_info["platform"],
        title=extracted.get("title") or "Submitted Claim",
        claims=[cv.model_dump() for cv in verified_claims],
        overall_verdict=scores["overall_verdict"],
        trust_score=scores["trust_score"]
    )
    source_graph_obj = SourceGraph(
        nodes=graph_data["nodes"],
        edges=graph_data["edges"]
    )

    # Construct Final Response Object
    result = AnalysisResult(
        id=analysis_id,
        url=user_url if user_url else None,
        input_text=user_text if user_text else None,
        platform=platform_info["platform"],
        domain=platform_info["domain"],
        source_type=platform_info["source_type"],
        title=extracted.get("title") or "Verified Content Analysis",
        extracted_content=extracted,
        overall_verdict=scores["overall_verdict"],
        verdict_badge=scores["verdict_badge"],
        trust_score=scores["trust_score"],
        confidence=scores["confidence"],
        source_credibility=cred_eval["score"],
        source_credibility_explanation=cred_eval["explanation"],
        claim_accuracy=scores["claim_accuracy"],
        evidence_strength=scores["evidence_strength"],
        manipulation_risk=scores["manipulation_risk"],
        score_disclaimer="AI-generated confidence estimate based on available evidence.",
        verdict_explanation=scores["verdict_explanation"],
        misinformation_type=misinfo_type,
        misinformation_type_explanation=misinfo_type_expl,
        claims=verified_claims,
        timeline_check=timeline_obj,
        original_source=original_source,
        related_sources=related_sources,
        image_analysis=image_result,
        source_graph=source_graph_obj,
        analysis_timestamp=now_dt.isoformat(),
        last_checked=now_dt.strftime("%B %d, %Y at %I:%M %p"),
        is_inaccessible_platform=False,
        inaccessible_message=None
    )

    # 12. Save to SQLite History
    save_analysis(result)

    return result

# Serve Frontend static assets
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
@app.get("/index.html")
async def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "TruVex AI API is running. Frontend assets not yet deployed."}

@app.get("/{filename}.{ext}")
async def serve_static_root(filename: str, ext: str):
    file_path = FRONTEND_DIR / f"{filename}.{ext}"
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")
