import re
from datetime import datetime
from typing import Dict, Any, Optional

CURRENT_YEAR = datetime.now().year

def check_timeline_recirculation(
    text: str,
    publication_date_str: Optional[str] = None,
    evidence_snippets: Optional[list] = None
) -> Dict[str, Any]:
    """
    Checks if older events/articles are being recirculated as breaking/current news.
    """
    combined_text = f"{text or ''} {' '.join([s.get('snippet', '') for s in (evidence_snippets or [])])}"
    
    # 1. Detect year references in text
    years_found = [int(y) for y in re.findall(r'\b(20[0-2][0-9])\b', combined_text)]
    
    # Check for breaking news urgency words
    has_urgency_words = bool(re.search(r'\b(breaking|just in|happening now|today|right now|alert|developing)\b', text or "", re.IGNORECASE))
    
    # Check publication date if available
    pub_year = None
    if publication_date_str:
        year_match = re.search(r'\b(20[0-2][0-9])\b', str(publication_date_str))
        if year_match:
            pub_year = int(year_match.group(1))

    # Check evidence dates for past debunking / coverage
    oldest_event_year = min(years_found) if years_found else pub_year

    # If the event is from more than 1 year ago and presented as breaking
    if oldest_event_year and oldest_event_year < CURRENT_YEAR - 1:
        if has_urgency_words or (pub_year and pub_year < CURRENT_YEAR - 1):
            return {
                "original_event_date": f"Circa {oldest_event_year}",
                "current_post_date": f"{pub_year or CURRENT_YEAR}",
                "is_old_recirculated": True,
                "warning_message": (
                    f"⚠️ POSSIBLE OLD NEWS RECIRCULATION: This content references an event originally reported around "
                    f"{oldest_event_year} (over {CURRENT_YEAR - oldest_event_year} years ago). Sharing archival footage "
                    "or past incidents without timestamp context can create false perceptions of an ongoing crisis."
                )
            }

    return {
        "original_event_date": str(pub_year or CURRENT_YEAR),
        "current_post_date": str(pub_year or CURRENT_YEAR),
        "is_old_recirculated": False,
        "warning_message": None
    }
