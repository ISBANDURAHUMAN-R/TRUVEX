import re
from urllib.parse import urlparse
from typing import Dict, Tuple

PLATFORM_PATTERNS = [
    (r"(?:https?:\/\/)?(?:www\.)?instagram\.com", "Instagram", "Social Media", True),
    (r"(?:https?:\/\/)?(?:chat\.)?whatsapp\.com|wa\.me", "WhatsApp", "Private Messaging", True),
    (r"(?:https?:\/\/)?(?:www\.|m\.)?facebook\.com|fb\.watch", "Facebook", "Social Media", True),
    (r"(?:https?:\/\/)?(?:www\.)?(?:twitter\.com|x\.com)", "X (formerly Twitter)", "Social Media", False),
    (r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)", "YouTube", "Video Platform", False),
    (r"(?:https?:\/\/)?(?:t\.me|telegram\.me)", "Telegram", "Messaging & Channels", False),
    (r"(?:https?:\/\/)?(?:www\.)?reddit\.com", "Reddit", "Social Forum", False),
    (r"(?:https?:\/\/)?(?:www\.)?tiktok\.com", "TikTok", "Short Video Platform", True),
    (r"(?:https?:\/\/)?(?:www\.)?threads\.net", "Threads", "Social Media", True),
    (r"(?:https?:\/\/)?(?:www\.)?linkedin\.com", "LinkedIn", "Professional Network", True),
]

KNOWN_NEWS_DOMAINS = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "nytimes.com", "wsj.com",
    "washingtonpost.com", "theguardian.com", "bloomberg.com", "cnn.com", "aljazeera.com",
    "nbcnews.com", "cbsnews.com", "abcnews.go.com", "foxnews.com", "npr.org",
    "politico.com", "thehill.com", "usatoday.com", "time.com", "economist.com",
    "forbes.com", "nature.com", "sciencemag.org", "scientificamerican.com", "nationalgeographic.com",
    "snopes.com", "politifact.com", "factcheck.org", "fullfact.org", "afp.com",
    "hindustantimes.com", "thehindu.com", "indianexpress.com", "ndtv.com", "indiatoday.in"
}

KNOWN_BLOG_DOMAINS = {
    "medium.com", "substack.com", "wordpress.com", "blogger.com", "blogspot.com", "tumblr.com"
}

def detect_platform(url: str = None, text: str = None) -> Dict[str, any]:
    """
    Detects platform, domain, and source type from a URL or text input.
    """
    if not url:
        # Fallback when only text is submitted
        return {
            "platform": "Direct Text Submission / Chat Forward",
            "domain": "user-input",
            "source_type": "Direct Text / WhatsApp Forward",
            "is_restricted": False,
            "guidance_message": None
        }

    clean_url = url.strip()
    parsed = urlparse(clean_url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]

    # Match social / video platforms
    for pattern, name, stype, is_restricted in PLATFORM_PATTERNS:
        if re.search(pattern, clean_url, re.IGNORECASE):
            guidance = None
            if is_restricted:
                guidance = (
                    f"Content could not be directly retrieved from {name} due to authentication "
                    "or private access restrictions. Please paste the text or upload a screenshot."
                )
            return {
                "platform": name,
                "domain": domain or name.lower(),
                "source_type": stype,
                "is_restricted": is_restricted,
                "guidance_message": guidance
            }

    # Check known blogs
    if any(domain.endswith(b) for b in KNOWN_BLOG_DOMAINS):
        return {
            "platform": "Blog / Independent Publication",
            "domain": domain,
            "source_type": "Blog",
            "is_restricted": False,
            "guidance_message": None
        }

    # Check known news outlets
    if any(domain.endswith(n) for n in KNOWN_NEWS_DOMAINS):
        return {
            "platform": "News Website",
            "domain": domain,
            "source_type": "News Website",
            "is_restricted": False,
            "guidance_message": None
        }

    # Generic website fallback
    source_type = "News / Content Website" if "news" in domain or "daily" in domain or "press" in domain else "Web Page"
    return {
        "platform": f"{domain.capitalize()} Web Source",
        "domain": domain,
        "source_type": source_type,
        "is_restricted": False,
        "guidance_message": None
    }
