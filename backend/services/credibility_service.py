from urllib.parse import urlparse
from typing import Dict, Any

# Curated database of reputable high-trust domains (Institutions, Wire Services, Fact Checkers)
HIGH_TRUST_SOURCES = {
    # Wire & Global News
    "reuters.com": (96, "Global news agency known for strict editorial verification, neutral wire reporting, and transparent corrections."),
    "apnews.com": (96, "Associated Press wire service with rigorous fact-checking standards and direct primary-source reporting."),
    "bbc.com": (92, "Public broadcaster with established editorial guidelines, global correspondents, and transparent corrections policy."),
    "bbc.co.uk": (92, "Public broadcaster with established editorial guidelines and high editorial standards."),
    "afp.com": (94, "Agence France-Presse international news agency with dedicated worldwide verification bureau."),
    "bloomberg.com": (90, "Financial and global news organization with rigorous data verification standards."),
    "npr.org": (90, "National Public Radio with public ombudsman, transparent corrections, and independent investigative journalism."),
    "theguardian.com": (88, "Major independent news organization with clear bylines, citations, and corrections log."),
    "nytimes.com": (88, "Established newspaper of record with thorough editorial oversight and public corrections."),
    "wsj.com": (89, "Established international business and news publication with high fact-checking standards."),
    "washingtonpost.com": (87, "Major publication with dedicated fact-checking team and detailed sourcing standards."),
    
    # Official Fact Checkers
    "snopes.com": (95, "Pioneering independent fact-checking organization adhering to IFCN ethical principles."),
    "politifact.com": (94, "Pulitzer-winning fact-checking organization with transparent sourcing and Truth-O-Meter methodologies."),
    "factcheck.org": (95, "Nonpartisan project of the Annenberg Public Policy Center dedicated to factual accuracy."),
    "fullfact.org": (94, "Independent UK fact-checking charity adhering to the International Fact-Checking Network code of principles."),
    "leadstories.com": (90, "Active fact-checking organization partnering with major platforms to debunk viral hoaxes."),
    "altnews.in": (92, "Dedicated fact-checking organization monitoring South Asian digital misinformation."),
    "boomlive.in": (92, "IFCN-certified fact-checking initiative tracking misinformation."),

    # Scientific & Medical
    "nature.com": (98, "Premier peer-reviewed scientific journal with rigorous academic referee review."),
    "sciencemag.org": (98, "Peer-reviewed academic journal published by the AAAS."),
    "science.org": (98, "Peer-reviewed academic journal published by the AAAS."),
    "nejm.org": (98, "The New England Journal of Medicine, premier peer-reviewed medical publication."),
    "thelancet.com": (97, "Leading peer-reviewed international medical journal."),
    "who.int": (96, "World Health Organization official scientific guidance and disease surveillance."),
    "cdc.gov": (96, "Centers for Disease Control and Prevention official health agency data."),
    "nasa.gov": (98, "National Aeronautics and Space Administration official scientific agency."),
    "nih.gov": (97, "National Institutes of Health official research publications and clinical databases."),
    "arxiv.org": (88, "Open-access research repository operated by Cornell University."),
}

# Satire websites (must be clearly identified so users are not misled)
SATIRE_DOMAINS = {
    "theonion.com": "Known satirical digital publication. Articles are humorous parodies and not factual news.",
    "babylonbee.com": "Known satirical site publishing conservative-leaning political and religious parody.",
    "waterfordwhispersnews.com": "Known Irish satirical website publishing parody articles.",
    "clickhole.com": "Known satirical website parodying clickbait media and viral internet culture.",
    "thebeaverton.com": "Known Canadian satirical news publication.",
    "newsthump.com": "Known UK satirical news site.",
    "thehardtimes.net": "Known satirical music and pop culture website.",
    "fakingnews.com": "Known Indian satirical news site.",
}

# High-risk TLDs and patterns often associated with disposable spam or imposter sites
SUSPICIOUS_TLDS = {".xyz", ".top", ".buzz", ".click", ".stream", ".icu", ".loan", ".win", ".bid"}

def evaluate_source_credibility(url: str = None, domain: str = None, has_author: bool = False, has_citations: bool = False) -> Dict[str, Any]:
    """
    Computes a 0-100 credibility score with rationale.
    Does NOT mark unknown sites as automatically fake.
    """
    if not domain and url:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

    if not domain or domain == "user-input":
        return {
            "score": 50,
            "rating": "UNVERIFIED SOURCE",
            "explanation": "Content was submitted directly as raw text or chat forward. Credibility is neutral (50/100) because there is no domain or institutional track record; factual claims must be verified solely on independent corroborating evidence."
        }

    # Clean domain
    domain_clean = domain.lower().strip()

    # 1. Check if it's a known Satire site
    for s_domain, s_reason in SATIRE_DOMAINS.items():
        if domain_clean == s_domain or domain_clean.endswith("." + s_domain):
            return {
                "score": 25,
                "rating": "SATIRE / PARODY",
                "explanation": f"{domain_clean} is recognized as a satirical publication: {s_reason}"
            }

    # 2. Check if it's a known high-trust source
    for ht_domain, (ht_score, ht_reason) in HIGH_TRUST_SOURCES.items():
        if domain_clean == ht_domain or domain_clean.endswith("." + ht_domain):
            return {
                "score": ht_score,
                "rating": "HIGH TRUST",
                "explanation": ht_reason
            }

    # 3. Check official Government or Educational TLDs
    if domain_clean.endswith(".gov") or domain_clean.endswith(".gov.uk") or domain_clean.endswith(".gov.in") or domain_clean.endswith(".gov.au"):
        return {
            "score": 95,
            "rating": "OFFICIAL GOVERNMENT",
            "explanation": "Official government domain (.gov). High institutional transparency, verifiable public statements, and legal accountability."
        }

    if domain_clean.endswith(".edu") or domain_clean.endswith(".ac.uk") or domain_clean.endswith(".edu.au"):
        return {
            "score": 92,
            "rating": "ACADEMIC / RESEARCH",
            "explanation": "Accredited higher education or academic institution domain (.edu). Strong adherence to peer-reviewed and scholarly standards."
        }

    # 4. Imposter / typosquatting checks (e.g. bbc-news-breaking.xyz, cnn-daily.top)
    target_brands = ["bbc", "cnn", "reuters", "nytimes", "nasa", "who", "cdc", "apnews"]
    is_imposter = False
    for brand in target_brands:
        if brand in domain_clean and not any(domain_clean.endswith(legit) for legit in [f"{brand}.com", f"{brand}.org", f"{brand}.gov", f"{brand}.co.uk"]):
            is_imposter = True
            break

    if is_imposter:
        return {
            "score": 20,
            "rating": "POTENTIAL IMPOSTER",
            "explanation": f"Domain '{domain_clean}' mimics the name of a reputable news agency ({brand.upper()}) on an unofficial domain structure, indicating potential impersonation or typosquatting."
        }

    # Check suspicious TLDs
    for stld in SUSPICIOUS_TLDS:
        if domain_clean.endswith(stld):
            return {
                "score": 38,
                "rating": "LOW TRUST DOMAIN",
                "explanation": f"Domain uses a generic high-spam TLD ({stld}) frequently associated with ephemeral or low-transparency clickbait sites."
            }

    # 5. Unknown or Independent Website (balanced evaluation)
    base_score = 62
    reasons = []

    if has_author:
        base_score += 8
        reasons.append("transparent author byline identified")
    else:
        base_score -= 4
        reasons.append("no clear author byline detected in extracted metadata")

    if has_citations:
        base_score += 8
        reasons.append("contains references or external citations")

    reasons.append("independent or lesser-known publisher without long-standing institutional ranking")

    score = max(35, min(75, base_score))
    explanation = f"Source evaluated at {score}/100: " + "; ".join(reasons) + ". Unknown sources are not automatically classified as fake, but their assertions must be cross-checked against independent evidence."

    return {
        "score": score,
        "rating": "MODERATE / INDEPENDENT",
        "explanation": explanation
    }
