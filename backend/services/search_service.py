import re
import asyncio
from urllib.parse import urlparse
from typing import List, Dict, Any
from backend.services.credibility_service import evaluate_source_credibility

try:
    from ddgs import DDGS
except ImportError:
    # Keep the API available when dependencies have not been installed yet.
    DDGS = None


def search_available() -> bool:
    return DDGS is not None

def generate_search_queries(claim: str) -> List[str]:
    """
    Generates intelligent search variations as mandated by Search Strategy:
    1. Direct search with fact-check keywords
    2. Debunk / hoax / myth targeted query
    3. Core entity keywords
    """
    cleaned = re.sub(r'[^\w\s-]', '', claim).strip()
    words = cleaned.split()
    
    queries = []
    
    # Query 1: Fact check search without exact quotes to avoid zero-matches
    queries.append(f"{cleaned[:70]} fact check")
    
    # Query 2: Debunk / hoax / myth search
    queries.append(f"{cleaned[:60]} hoax OR debunked OR myth")
    
    # Query 3: Core keywords search
    if len(words) > 3:
        filtered = [w for w in words if w.lower() not in {"has", "have", "been", "that", "this", "with", "from", "will", "what", "which", "after", "and", "the", "for", "are"}]
        queries.append(" ".join(filtered[:6]))
    else:
        queries.append(cleaned)
        
    return queries[:3]

def run_ddgs_query(query: str, max_results: int = 4) -> List[Dict[str, Any]]:
    """Runs a single query synchronously via DDGS."""
    if DDGS is None:
        return []

    results = []
    try:
        ddgs = DDGS()
        raw = list(ddgs.text(query, max_results=max_results))
        for item in raw:
            title = item.get("title", "").strip()
            link = item.get("href", "").strip()
            body = item.get("body", "").strip()
            if title and link and link.startswith("http"):
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": body
                })
    except Exception:
        # Gracefully handle transient network errors
        pass
    return results

async def search_evidence_for_claim(claim: str, max_sources: int = 6) -> List[Dict[str, Any]]:
    """
    Executes multi-query search asynchronously, deduplicates results,
    and enriches with domain credibility scores and source types.
    Strictly uses real returned URLs (Anti-Hallucination).
    """
    queries = generate_search_queries(claim)
    
    # Run searches in threadpool to keep FastAPI async loop non-blocking
    loop = asyncio.get_event_loop()
    all_raw_results = []
    
    for q in queries:
        res = await loop.run_in_executor(None, run_ddgs_query, q, 4)
        all_raw_results.extend(res)

    # Deduplicate by domain and normalized URL
    seen_urls = set()
    seen_domains = {}
    enriched_results = []

    for item in all_raw_results:
        url = item["url"]
        if url in seen_urls:
            continue
        seen_urls.add(url)

        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        # Limit max 2 articles from same domain for diversity
        if seen_domains.get(domain, 0) >= 2:
            continue
        seen_domains[domain] = seen_domains.get(domain, 0) + 1

        # Evaluate domain credibility
        cred_eval = evaluate_source_credibility(url=url, domain=domain)
        
        # Determine source type classification
        source_type = "Reputable News"
        if "factcheck" in domain or "snopes" in domain or "politifact" in domain or "leadstories" in domain:
            source_type = "Fact-Checking Organization"
        elif domain.endswith(".gov") or domain.endswith(".gov.uk"):
            source_type = "Official Government Body"
        elif domain.endswith(".edu") or "nature.com" in domain or "science.org" in domain:
            source_type = "Scientific / Academic Institution"
        elif domain in ["reuters.com", "apnews.com", "afp.com"]:
            source_type = "International Wire Service"
        elif cred_eval["rating"] == "SATIRE / PARODY":
            source_type = "Satire / Parody"
        elif cred_eval["score"] < 40:
            source_type = "Unverified / Low Trust Blog"

        enriched_results.append({
            "title": item["title"],
            "url": url,
            "domain": domain,
            "snippet": item["snippet"],
            "credibility_score": cred_eval["score"],
            "credibility_rating": cred_eval["rating"],
            "source_type": source_type
        })

    # Sort results by credibility score descending so high-trust sources appear first
    enriched_results.sort(key=lambda x: x["credibility_score"], reverse=True)
    return enriched_results[:max_sources]
