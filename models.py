from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    url: Optional[str] = Field(None, description="The URL of the news, post, or media to analyze")
    text: Optional[str] = Field(None, description="Fallback or pasted news text")
    image_base64: Optional[str] = Field(None, description="Optional base64 encoded screenshot or image")
    api_key: Optional[str] = Field(None, description="Optional custom Gemini API key")

class EvidenceItem(BaseModel):
    source_name: str
    source_domain: str
    title: str
    explanation: str
    link: str
    source_type: str = "Reputable News"
    credibility_score: int = 85

class ClaimVerification(BaseModel):
    claim: str
    verdict: str  # TRUE, MOSTLY TRUE, MISLEADING, UNVERIFIED, MOSTLY FALSE, FALSE
    confidence: int  # 0 - 100
    why: str
    supporting_evidence: List[EvidenceItem] = []
    contradicting_evidence: List[EvidenceItem] = []

class RelatedNews(BaseModel):
    title: str
    website: str
    publication_date: Optional[str] = None
    description: str
    source_credibility: int = 80
    link: str

class OriginalSource(BaseModel):
    source_name: str
    date: Optional[str] = None
    link: Optional[str] = None
    evidence_rationale: str

class TimelineCheck(BaseModel):
    original_event_date: Optional[str] = None
    current_post_date: Optional[str] = None
    is_old_recirculated: bool = False
    warning_message: Optional[str] = None

class ImageAnalysisResult(BaseModel):
    status: str  # "Genuine", "Misleadingly captioned", "Potentially manipulated", etc.
    manipulation_risk: str  # Low, Medium, High, Inconclusive
    exif_details: Dict[str, Any] = {}
    forensic_notes: str

class GraphNode(BaseModel):
    id: str
    label: str
    category: str  # url, platform, content, claim, source, verdict
    status: Optional[str] = None  # true, false, misleading, unverified, neutral
    score: Optional[int] = None

class GraphEdge(BaseModel):
    source: str
    target: str
    label: str
    relation: str  # supports, contradicts, extracts, derived_from

class SourceGraph(BaseModel):
    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []

class AnalysisResult(BaseModel):
    id: str
    url: Optional[str] = None
    input_text: Optional[str] = None
    platform: str
    domain: str
    source_type: str  # Social Media, News Website, Blog, Video Platform, Messaging Chat, Other
    title: str
    extracted_content: Dict[str, Any] = {}
    
    # Core Verdict & Scores
    overall_verdict: str  # 🟢 LIKELY TRUE, 🟡 MOSTLY TRUE, 🟠 MISLEADING, 🔴 LIKELY FALSE, ⚪ UNVERIFIED
    verdict_badge: str    # "LIKELY TRUE", "MOSTLY TRUE", "MISLEADING", "LIKELY FALSE", "UNVERIFIED"
    trust_score: int      # 0-100
    confidence: int       # 0-100
    
    # Sub-scores
    source_credibility: int  # 0-100
    source_credibility_explanation: str
    claim_accuracy: int      # 0-100
    evidence_strength: int   # 0-100
    manipulation_risk: int   # 0-100
    score_disclaimer: str = "AI-generated confidence estimate based on available evidence."
    
    # Explanations & Claims
    verdict_explanation: str
    misinformation_type: str
    misinformation_type_explanation: str
    claims: List[ClaimVerification] = []
    
    # Extended investigations
    timeline_check: TimelineCheck
    original_source: Optional[OriginalSource] = None
    related_sources: List[RelatedNews] = []
    image_analysis: Optional[ImageAnalysisResult] = None
    source_graph: SourceGraph
    
    # Metadata & Platform guidance
    analysis_timestamp: str
    last_checked: str
    is_inaccessible_platform: bool = False
    inaccessible_message: Optional[str] = None

class HistorySummary(BaseModel):
    id: str
    url: Optional[str]
    title: str
    platform: str
    verdict: str
    trust_score: int
    confidence: int
    analysis_timestamp: str
