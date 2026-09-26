import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from backend.config import GEMINI_API_KEY
from backend.models import ClaimVerification, EvidenceItem, RelatedNews, OriginalSource

# High-signal debunk keywords that indicate contradiction
DEBUNK_KEYWORDS = [
    "false", "hoax", "debunk", "misleading", "fake", "incorrect", "untrue", "refuted",
    "no evidence", "unsubstantiated", "fabricat", "inaccurate", "denies", "denied", "satire",
    "myth", "myths", "unproven", "no proof", "disproven", "disproved", "cannot cure", "does not cure",
    "magic bullet", "scam", "rumor", "rumour", "doubtful", "unsupported", "exaggerated", "misrepresented",
    "bogus", "conspiracy", "pseudoscientific", "pseudoscience", "unscientific"
]

# High-signal confirmation keywords that indicate support
SUPPORT_KEYWORDS = [
    "confirms", "confirmed", "verified", "announced", "official statement", "proves", "proven",
    "true", "reports that", "agrees", "published study", "findings show", "authoritative data",
    "detects", "detected", "detection", "finds", "found", "discovers", "discovered", "discovery",
    "reveals", "revealed", "shows", "showed", "observes", "observed", "evidence of", "measurements by",
    "recorded", "documents", "published in"
]

CLAIM_STOPWORDS = {
    "about", "after", "also", "been", "being", "from", "have", "into", "more",
    "over", "said", "that", "the", "their", "there", "these", "they", "this",
    "those", "through", "under", "were", "what", "when", "where", "which",
    "while", "with", "would", "located", "confirmed", "according", "reported",
}

def analyze_stance_heuristics(claim: str, snippet: str, title: str, credibility_score: int = 80) -> str:
    """
    Evaluates whether an evidence item supports, contradicts, or is neutral/contextual to a claim.
    """
    text = f"{title} {snippet}".lower()
    claim_terms = [
        term for term in re.findall(r"[a-z0-9]+", claim.lower())
        if len(term) > 3 and term not in CLAIM_STOPWORDS
    ]

    if not claim_terms:
        return "unrelated"

    # Only compare evidence that shares most of the claim's meaningful terms.
    # This prevents a generic "debunked" headline about a nearby topic from
    # being treated as a direct contradiction.
    overlap = sum(1 for term in set(claim_terms) if re.search(r"\b" + re.escape(term) + r"\b", text))
    required_overlap = min(2, len(set(claim_terms)))
    if overlap < required_overlap or overlap / len(set(claim_terms)) < 0.65:
        return "unrelated"

    # Unranked sites can provide context, but should not decide a verdict.
    if credibility_score < 75:
        return "neutral_context"
    
    # Check for debunking signals
    debunk_hits = sum(1 for kw in DEBUNK_KEYWORDS if re.search(r'\b' + kw, text))
    
    # Check for support signals
    support_hits = sum(1 for kw in SUPPORT_KEYWORDS if re.search(r'\b' + kw, text))

    if debunk_hits > support_hits and debunk_hits >= 1:
        return "contradicts"
    elif support_hits > debunk_hits and support_hits >= 1:
        return "supports"
    else:
        # Contextual relevance & corroboration check
        # If no debunk signals, high-trust source, and high entity overlap -> corroborates!
        if debunk_hits == 0 and credibility_score >= 85:
            return "supports"
        return "neutral_context"

def verify_single_claim_rule_based(claim: str, search_results: List[Dict[str, Any]]) -> ClaimVerification:
    """
    Evaluates a single claim against real search results without an LLM.
    Strictly uses real evidence and never invents links.
    """
    if not search_results:
        return ClaimVerification(
            claim=claim,
            verdict="UNVERIFIED",
            confidence=40,
            why="No authoritative reports or independent evidence could be retrieved matching this claim. The assertion remains unverified.",
            supporting_evidence=[],
            contradicting_evidence=[]
        )

    supporting = []
    contradicting = []
    
    for item in search_results:
        stance = analyze_stance_heuristics(claim, item.get("snippet", ""), item.get("title", ""), item.get("credibility_score", 80))
        
        # High-credibility fact-checking sites debunking it
        if item.get("source_type") == "Fact-Checking Organization" and item.get("credibility_score", 0) >= 75 and stance not in {"unrelated", "neutral_context"}:
            if any(w in (item["title"] + " " + item["snippet"]).lower() for w in ["false", "misleading", "hoax", "fake"]):
                stance = "contradicts"
            elif "true" in (item["title"] + " " + item["snippet"]).lower():
                stance = "supports"

        evidence_obj = EvidenceItem(
            source_name=item.get("domain", "").capitalize(),
            source_domain=item.get("domain", ""),
            title=item.get("title", "News Report"),
            explanation=item.get("snippet", "Evidence extracted from source."),
            link=item.get("url", "#"),
            source_type=item.get("source_type", "Reputable News"),
            credibility_score=item.get("credibility_score", 80)
        )

        if stance == "contradicts":
            contradicting.append(evidence_obj)
        elif stance == "supports":
            supporting.append(evidence_obj)

    # Sensationalism / miracle cure red flag check in claim text
    has_sensational_red_flag = bool(re.search(r'\b(cures all|100% cure|10,000 times|secret cure|miracle cure|doctors are hiding|pharma is hiding)\b', claim, re.I))

    # Determine verdict and confidence
    num_contra = len(contradicting)
    num_supp = len(supporting)

    if num_contra > 0 and num_supp == 0:
        verdict = "FALSE" if num_contra >= 2 else "MOSTLY FALSE"
        confidence = min(96, 75 + (num_contra * 10))
        why = f"Multiple reliable sources report facts that directly contradict this claim. Debunking analyses and official statements dispute the reported narrative."
    elif num_contra > 0 and num_supp > 0:
        verdict = "MISLEADING"
        confidence = 88
        why = f"The claim mixes elements of truth with unsubstantiated or exaggerated details. While some sources acknowledge related events, reliable verification disputes the core sensationalized assertion."
    elif num_supp >= 2:
        verdict = "TRUE" if num_supp >= 3 else "MOSTLY TRUE"
        confidence = min(95, 78 + (num_supp * 8))
        why = f"Independent reporting and authoritative institutional sources corroborate the primary assertions of this claim."
    elif num_supp == 1:
        verdict = "MOSTLY TRUE"
        confidence = 72
        why = f"Preliminary reporting aligns with the claim, though broader multi-source corroboration is still developing."
    else:
        verdict = "UNVERIFIED"
        confidence = 50
        if has_sensational_red_flag:
            why = "This claim uses extraordinary medical language, but no authoritative supporting or contradicting source was retrieved. It remains unverified."
        else:
            why = "Available independent sources do not provide conclusive proof either affirming or denying this specific claim."

    return ClaimVerification(
        claim=claim,
        verdict=verdict,
        confidence=confidence,
        why=why,
        supporting_evidence=supporting[:3],
        contradicting_evidence=contradicting[:3]
    )

async def verify_claim_with_gemini(claim: str, search_results: List[Dict[str, Any]], api_key: str) -> ClaimVerification:
    """
    Uses Gemini API to synthesize claims and evidence with high semantic nuance.
    Strictly preserves real URLs from search_results.
    """
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        evidence_digest = []
        for i, r in enumerate(search_results[:5]):
            evidence_digest.append(f"[{i+1}] Title: {r['title']}\nSource: {r['domain']}\nSnippet: {r['snippet']}\nURL: {r['url']}")
        
        digest_str = "\n\n".join(evidence_digest)
        
        prompt = f"""
You are TruVex AI Fact-Checking Engine.
Analyze the following claim strictly against the provided real web search evidence.

CLAIM:
"{claim}"

REAL SEARCH EVIDENCE:
{digest_str}

TASK:
1. Determine the verdict. Must be one of: TRUE, MOSTLY TRUE, MISLEADING, UNVERIFIED, MOSTLY FALSE, FALSE.
2. Provide a confidence score (integer 0-100).
3. Write a clear, simple, human-friendly explanation of WHY (no technical jargon).
4. Identify which evidence indices (e.g. 1, 2) SUPPORT the claim, and which CONTRADICT the claim.

Return your response in this exact format:
VERDICT: [Verdict]
CONFIDENCE: [Number]
WHY: [Explanation]
SUPPORTING_INDICES: [comma separated numbers or 'NONE']
CONTRADICTING_INDICES: [comma separated numbers or 'NONE']
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text.strip()
        
        v_match = re.search(r'VERDICT:\s*(TRUE|MOSTLY TRUE|MISLEADING|UNVERIFIED|MOSTLY FALSE|FALSE)', text, re.I)
        c_match = re.search(r'CONFIDENCE:\s*(\d+)', text)
        w_match = re.search(r'WHY:\s*(.+?)(?=SUPPORTING_INDICES:|$)', text, re.DOTALL | re.I)
        supp_match = re.search(r'SUPPORTING_INDICES:\s*([0-9,\s]+)', text, re.I)
        contra_match = re.search(r'CONTRADICTING_INDICES:\s*([0-9,\s]+)', text, re.I)

        verdict = v_match.group(1).upper() if v_match else "UNVERIFIED"
        confidence = int(c_match.group(1)) if c_match else 75
        why = w_match.group(1).strip() if w_match else "Analysis concluded based on independent web search evidence."

        supporting = []
        contradicting = []

        if supp_match:
            for idx_str in supp_match.group(1).split(","):
                try:
                    idx = int(idx_str.strip()) - 1
                    if 0 <= idx < len(search_results):
                        r = search_results[idx]
                        supporting.append(EvidenceItem(
                            source_name=r["domain"].capitalize(),
                            source_domain=r["domain"],
                            title=r["title"],
                            explanation=r["snippet"][:180] + "...",
                            link=r["url"],
                            source_type=r["source_type"],
                            credibility_score=r["credibility_score"]
                        ))
                except Exception:
                    pass

        if contra_match:
            for idx_str in contra_match.group(1).split(","):
                try:
                    idx = int(idx_str.strip()) - 1
                    if 0 <= idx < len(search_results):
                        r = search_results[idx]
                        contradicting.append(EvidenceItem(
                            source_name=r["domain"].capitalize(),
                            source_domain=r["domain"],
                            title=r["title"],
                            explanation=r["snippet"][:180] + "...",
                            link=r["url"],
                            source_type=r["source_type"],
                            credibility_score=r["credibility_score"]
                        ))
                except Exception:
                    pass

        return ClaimVerification(
            claim=claim,
            verdict=verdict,
            confidence=confidence,
            why=why,
            supporting_evidence=supporting[:3],
            contradicting_evidence=contradicting[:3]
        )

    except Exception:
        # Fallback to rule-based verification
        return verify_single_claim_rule_based(claim, search_results)

def calculate_overall_scores(
    claims_verified: List[ClaimVerification],
    source_credibility: int,
    is_old_recirculated: bool = False
) -> Dict[str, Any]:
    """
    Calculates overall trust score, claim accuracy, evidence strength, manipulation risk,
    and the final overall verdict banner.
    """
    if not claims_verified:
        return {
            "overall_verdict": "⚪ UNVERIFIED",
            "verdict_badge": "UNVERIFIED",
            "trust_score": 50,
            "confidence": 50,
            "claim_accuracy": 50,
            "evidence_strength": 30,
            "manipulation_risk": 50,
            "verdict_explanation": "Insufficient verifiable claims could be extracted to reach a definitive trust evaluation."
        }

    # Weight claim verdicts
    verdict_weights = {
        "TRUE": 100,
        "MOSTLY TRUE": 80,
        "MISLEADING": 40,
        "UNVERIFIED": 50,
        "MOSTLY FALSE": 20,
        "FALSE": 0
    }

    claim_scores = [verdict_weights.get(cv.verdict, 50) for cv in claims_verified]
    claim_accuracy = int(sum(claim_scores) / len(claim_scores))
    
    # Evidence strength based on number of independent supporting/contradicting sources
    total_sources = sum(len(cv.supporting_evidence) + len(cv.contradicting_evidence) for cv in claims_verified)
    evidence_strength = min(95, max(30, 45 + (total_sources * 9)))
    
    # Average confidence
    confidence = int(sum(cv.confidence for cv in claims_verified) / len(claims_verified))

    # Overall Trust Score (composite of claim accuracy 60%, source credibility 30%, evidence strength 10%)
    trust_score = int((claim_accuracy * 0.55) + (source_credibility * 0.35) + (evidence_strength * 0.10))
    
    # If old news is recirculated as breaking, apply manipulation penalty
    manipulation_risk = 100 - trust_score
    if is_old_recirculated:
        trust_score = max(15, trust_score - 20)
        manipulation_risk = min(95, manipulation_risk + 30)

    # Determine Final Verdict Banner
    false_count = sum(1 for cv in claims_verified if cv.verdict in ["FALSE", "MOSTLY FALSE"])
    true_count = sum(1 for cv in claims_verified if cv.verdict in ["TRUE", "MOSTLY TRUE"])
    misleading_count = sum(1 for cv in claims_verified if cv.verdict == "MISLEADING")

    if false_count >= 1 and false_count >= true_count:
        overall_verdict = "🔴 LIKELY FALSE"
        verdict_badge = "LIKELY FALSE"
        explanation = f"Fact-checking across independent sources reveals that key factual claims in this content are inaccurate or fabricated."
    elif misleading_count >= 1 or (true_count > 0 and false_count > 0):
        overall_verdict = "🟠 MISLEADING"
        verdict_badge = "MISLEADING"
        explanation = f"The content contains elements of real events, but presents them with exaggerated framing, missing context, or unverified claims."
    elif true_count >= 1 and false_count == 0:
        if trust_score >= 80:
            overall_verdict = "🟢 LIKELY TRUE"
            verdict_badge = "LIKELY TRUE"
        else:
            overall_verdict = "🟡 MOSTLY TRUE"
            verdict_badge = "MOSTLY TRUE"
        explanation = f"The core factual claims are corroborated by independent reporting and authoritative public sources."
    else:
        overall_verdict = "⚪ UNVERIFIED"
        verdict_badge = "UNVERIFIED"
        explanation = f"Current independent evidence is insufficient to verify the authenticity of these assertions. The claim is unverified."

    if is_old_recirculated:
        overall_verdict = "🟠 MISLEADING"
        verdict_badge = "MISLEADING"
        explanation += " Additionally, this content recirculates archival material as though it were a current breaking event."

    return {
        "overall_verdict": overall_verdict,
        "verdict_badge": verdict_badge,
        "trust_score": trust_score,
        "confidence": confidence,
        "claim_accuracy": claim_accuracy,
        "evidence_strength": evidence_strength,
        "manipulation_risk": manipulation_risk,
        "verdict_explanation": explanation
    }

def classify_misinformation_type(
    verdict_badge: str,
    is_old_recirculated: bool,
    claims_verified: List[ClaimVerification],
    source_rating: str
) -> Tuple[str, str]:
    """
    Classifies the specific category of misinformation as required by Section 12.
    """
    if source_rating == "SATIRE / PARODY":
        return "Satire / Parody", "Content originated from a known satirical source intended for humor rather than factual reporting."
    if source_rating == "POTENTIAL IMPOSTER":
        return "Impersonation", "The publishing domain mimics a reputable organization to mislead readers about its authority."
    if is_old_recirculated:
        return "Old news presented as new", "Archival footage or past event reports are being shared as contemporary breaking news."
    
    if verdict_badge == "LIKELY FALSE":
        return "False information", "The assertions presented have been directly refuted by reliable independent reporting."
    elif verdict_badge == "MISLEADING":
        return "Out-of-context information", "Real occurrences are reframed with sensationalized assertions or omitted crucial caveats."
    elif verdict_badge in ["LIKELY TRUE", "MOSTLY TRUE"]:
        return "Genuine information", "Factual assertions correspond with verifiable public records and independent news reports."
    else:
        return "Unverified claim", "The assertions lack sufficient corroborating documentation to confirm or refute."

def discover_original_source(search_results: List[Dict[str, Any]]) -> Optional[OriginalSource]:
    """
    Discovers the earliest or most authoritative primary source from the evidence collection.
    Section 11 requirement.
    """
    # Look for wire service or official source
    authoritative = [r for r in search_results if r.get("source_type") in ["Official Government Body", "International Wire Service", "Scientific / Academic Institution"]]
    if authoritative:
        top = authoritative[0]
        return OriginalSource(
            source_name=top["domain"].capitalize(),
            date="Primary Record",
            link=top["url"],
            evidence_rationale=f"Primary coverage originated or was definitively confirmed by {top['domain']} based on institutional reporting."
        )
    elif search_results:
        top = search_results[0]
        return OriginalSource(
            source_name=top["domain"].capitalize(),
            date="Earliest Indexed Record",
            link=top["url"],
            evidence_rationale=f"Earliest verified independent reporting detected on {top['domain']}."
        )
    return None

def extract_related_news(search_results: List[Dict[str, Any]], max_items: int = 4) -> List[RelatedNews]:
    """
    Extracts distinct independent related news articles as required by Section 10.
    """
    related = []
    seen = set()
    for r in search_results:
        domain = r.get("domain", "")
        if domain in seen or r.get("source_type") == "Satire / Parody":
            continue
        seen.add(domain)
        related.append(RelatedNews(
            title=r.get("title", "Related Coverage"),
            website=domain.capitalize(),
            publication_date="Recent",
            description=r.get("snippet", "")[:160] + "...",
            source_credibility=r.get("credibility_score", 80),
            link=r.get("url", "#")
        ))
        if len(related) >= max_items:
            break
    return related
