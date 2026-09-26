import re
from typing import List, Optional
from backend.config import GEMINI_API_KEY

def clean_sentence_for_claim(sentence: str) -> str:
    """Cleans punctuation, conversational artifacts, and trims whitespace."""
    s = sentence.strip()
    s = re.sub(r'^(breaking|alert|exclusive|urgent|watch|shocking|must read)[:\s!*-]+', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def extract_claims_rule_based(title: str, text: str, max_claims: int = 3) -> List[str]:
    """
    Intelligently extracts testable factual claims from headline and text without an external LLM.
    Identifies high-signal sentences with named entities, dates, quotes, or action verbs.
    """
    claims = []
    
    IGNORED_TITLE_PREFIXES = (
        "unable to access", "connection failed", "extraction error",
        "restricted access", "direct text", "untitled web", "content from",
        "page not found", "access denied", "403", "404", "error"
    )

    # 1. Headline is almost always a primary claim (unless it's an error/placeholder title)
    if title and len(title.strip()) > 10:
        cleaned_title = clean_sentence_for_claim(title)
        lower_title = cleaned_title.lower()
        if not any(lower_title.startswith(p) for p in IGNORED_TITLE_PREFIXES) and len(cleaned_title) > 15:
            claims.append(cleaned_title)

    # 2. Extract key sentences from body text
    combined_text = (text or "").strip()
    if combined_text:
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', combined_text)
        
        # High value indicators for factual assertions
        assertion_patterns = [
            r"\b(confirmed|announced|discovered|warned|stated|proved|passed|banned|died|killed|signed|claimed)\b",
            r"\b(nasa|who|cdc|government|president|minister|court|police|scientists|study|university)\b",
            r"\b(\d+%\s*|\$\d+|\d+\s*(people|deaths|cases|miles|km|years))\b",
            r"\b(according to|official report|new law|breakthrough)\b"
        ]

        for s in sentences:
            s_clean = clean_sentence_for_claim(s)
            if len(s_clean) < 25 or len(s_clean) > 250:
                continue
            
            # Avoid repeating the title
            if claims and any(c.lower() in s_clean.lower() or s_clean.lower() in c.lower() for c in claims):
                continue

            # Check if sentence contains verifiable factual assertion
            if any(re.search(pat, s_clean, re.IGNORECASE) for pat in assertion_patterns):
                claims.append(s_clean)
                if len(claims) >= max_claims:
                    break

        # Fallback if no specific assertion pattern matched but sentences exist
        if len(claims) < max_claims:
            for s in sentences:
                s_clean = clean_sentence_for_claim(s)
                if 25 <= len(s_clean) <= 200 and not any(s_clean.lower() in c.lower() for c in claims):
                    claims.append(s_clean)
                    if len(claims) >= max_claims:
                        break

    # If still no claims extracted, use the title or short text snippet
    if not claims:
        fallback = (title or text or "").strip()[:140]
        if fallback:
            claims.append(fallback)
        else:
            claims.append("Unspecified factual assertion in submitted media")

    return claims[:max_claims]

async def extract_claims_ai(title: str, text: str, api_key: Optional[str] = None, max_claims: int = 3) -> List[str]:
    """
    Uses Gemini API to extract atomic factual claims if an API key is available,
    otherwise gracefully falls back to deterministic rule-based extractor.
    """
    effective_key = api_key or GEMINI_API_KEY
    if not effective_key:
        return extract_claims_rule_based(title, text, max_claims)

    try:
        from google import genai
        client = genai.Client(api_key=effective_key)
        
        prompt = f"""
You are TruVex AI Claim Extraction Engine.
Extract up to {max_claims} distinct, verifiable, factual claims from the following headline and text.
Rules:
1. Extract only factual claims that can be proven or disproven by independent evidence.
2. Exclude rhetorical questions, pure subjective opinions, and emotional hyperbole.
3. Make each claim self-contained and clear.
4. Return ONLY a plain list of claims, one per line, starting with a dash (-).

HEADLINE:
{title}

CONTENT:
{text[:2000]}
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        lines = response.text.strip().split("\n")
        extracted = []
        for line in lines:
            line_clean = re.sub(r'^[\s*\-•\d.]+', '', line).strip()
            if line_clean and len(line_clean) > 10:
                extracted.append(line_clean)
        
        if extracted:
            return extracted[:max_claims]

    except Exception:
        # Graceful fallback to rule-based extractor if API call errors or rate-limits
        pass

    return extract_claims_rule_based(title, text, max_claims)
