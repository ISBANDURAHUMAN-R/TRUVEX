import json
import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, Any, Optional
from backend.config import USER_AGENT, REQUEST_TIMEOUT
from backend.services.platform_detector import detect_platform

async def extract_content_from_url(url: str) -> Dict[str, Any]:
    """
    Extracts metadata, article text, author, and date from a given URL.
    Respects access boundaries and never fabricates content.
    """
    platform_info = detect_platform(url)

    # Inaccessible / restricted platforms check
    if platform_info["is_restricted"]:
        return {
            "title": f"Content from {platform_info['platform']}",
            "text": "",
            "description": "",
            "author": None,
            "publication_date": None,
            "image_url": None,
            "video_url": None,
            "has_citations": False,
            "is_inaccessible": True,
            "platform_info": platform_info,
            "inaccessible_message": platform_info["guidance_message"]
        }

    # Handle YouTube URLs via public oEmbed
    if platform_info["platform"] == "YouTube":
        return await extract_youtube_metadata(url, platform_info)

    # Standard Web / News extraction
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            # Check for paywalls or restricted status codes
            if response.status_code in [401, 403]:
                return {
                    "title": "Restricted Access Page",
                    "text": "",
                    "description": "",
                    "author": None,
                    "publication_date": None,
                    "image_url": None,
                    "video_url": None,
                    "has_citations": False,
                    "is_inaccessible": True,
                    "platform_info": platform_info,
                    "inaccessible_message": f"This page returned HTTP {response.status_code} (Access Restricted/Paywalled). Please paste the article text directly or upload a screenshot."
                }
            
            if response.status_code != 200:
                return {
                    "title": "Unable to access page",
                    "text": "",
                    "description": "",
                    "author": None,
                    "publication_date": None,
                    "image_url": None,
                    "video_url": None,
                    "has_citations": False,
                    "is_inaccessible": True,
                    "platform_info": platform_info,
                    "inaccessible_message": f"Received HTTP status code {response.status_code} from {platform_info['domain']}. Please provide the copied text or an alternative link."
                }

            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # 1. Headline / Title
            title = ""
            og_title = soup.find("meta", property="og:title")
            twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
            h1 = soup.find("h1")
            
            if og_title and og_title.get("content"):
                title = og_title["content"].strip()
            elif twitter_title and twitter_title.get("content"):
                title = twitter_title["content"].strip()
            elif h1:
                title = h1.get_text().strip()
            elif soup.title:
                title = soup.title.get_text().strip()

            # 2. Description
            description = ""
            og_desc = soup.find("meta", property="og:description")
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if og_desc and og_desc.get("content"):
                description = og_desc["content"].strip()
            elif meta_desc and meta_desc.get("content"):
                description = meta_desc["content"].strip()

            # 3. Image
            image_url = None
            og_img = soup.find("meta", property="og:image")
            if og_img and og_img.get("content"):
                image_url = og_img["content"]

            # 4. Author
            author = None
            author_meta = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", property="article:author")
            if author_meta and author_meta.get("content"):
                author = author_meta["content"].strip()
            else:
                byline = soup.find(class_=re.compile(r"byline|author|writer", re.I))
                if byline:
                    author = byline.get_text().strip()

            # 5. Publication Date
            pub_date = None
            date_meta = (
                soup.find("meta", property="article:published_time") or
                soup.find("meta", attrs={"name": "publication_date"}) or
                soup.find("meta", attrs={"name": "date"}) or
                soup.find("meta", property="og:published_time")
            )
            if date_meta and date_meta.get("content"):
                pub_date = date_meta["content"].strip()
            else:
                time_tag = soup.find("time")
                if time_tag and time_tag.get("datetime"):
                    pub_date = time_tag["datetime"]
                elif time_tag:
                    pub_date = time_tag.get_text().strip()

            # 6. JSON-LD structured data parsing
            json_ld_scripts = soup.find_all("script", type="application/ld+json")
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string or "{}")
                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]
                    if isinstance(data, dict):
                        if not title and data.get("headline"):
                            title = data.get("headline")
                        if not pub_date and data.get("datePublished"):
                            pub_date = data.get("datePublished")
                        if not author and data.get("author"):
                            auth = data.get("author")
                            if isinstance(auth, dict):
                                author = auth.get("name")
                            elif isinstance(auth, list) and len(auth) > 0 and isinstance(auth[0], dict):
                                author = auth[0].get("name")
                except Exception:
                    pass

            # 7. Article text extraction
            paragraphs = []
            article_tag = soup.find("article") or soup.find("main") or soup.find(id=re.compile(r"article|content|post", re.I))
            source_container = article_tag if article_tag else soup

            for p in source_container.find_all("p"):
                p_text = p.get_text().strip()
                # Exclude boilerplate / navigation crumbs
                if len(p_text) > 35 and not re.search(r"cookie|privacy policy|terms of service|subscribe|sign in|all rights reserved", p_text, re.I):
                    paragraphs.append(p_text)

            body_text = "\n\n".join(paragraphs[:15])  # Cap at first 15 substantive paragraphs

            # Citations check
            has_citations = len(source_container.find_all("a", href=True)) >= 3

            return {
                "title": title or "Untitled Web Article",
                "text": body_text,
                "description": description,
                "author": author,
                "publication_date": pub_date,
                "image_url": image_url,
                "video_url": None,
                "has_citations": has_citations,
                "is_inaccessible": False,
                "platform_info": platform_info,
                "inaccessible_message": None
            }

    except httpx.ConnectError:
        return {
            "title": "Connection Failed",
            "text": "",
            "description": "",
            "author": None,
            "publication_date": None,
            "image_url": None,
            "video_url": None,
            "has_citations": False,
            "is_inaccessible": True,
            "platform_info": platform_info,
            "inaccessible_message": f"Could not connect to {platform_info['domain']}. The domain may be offline, restricted, or blocked by firewalls. Please paste the text or screenshot."
        }
    except Exception as e:
        return {
            "title": "Extraction Error",
            "text": "",
            "description": "",
            "author": None,
            "publication_date": None,
            "image_url": None,
            "video_url": None,
            "has_citations": False,
            "is_inaccessible": True,
            "platform_info": platform_info,
            "inaccessible_message": f"Unable to automatically extract page content: {str(e)}. Please paste the text or upload a screenshot."
        }

async def extract_youtube_metadata(url: str, platform_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts YouTube video details using the public YouTube oEmbed endpoint.
    """
    try:
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            res = await client.get(oembed_url)
            if res.status_code == 200:
                data = res.json()
                title = data.get("title", "YouTube Video")
                author = data.get("author_name")
                thumbnail = data.get("thumbnail_url")
                return {
                    "title": title,
                    "text": f"YouTube Video by channel '{author}': {title}",
                    "description": f"Video by {author}",
                    "author": author,
                    "publication_date": None,
                    "image_url": thumbnail,
                    "video_url": url,
                    "has_citations": False,
                    "is_inaccessible": False,
                    "platform_info": platform_info,
                    "inaccessible_message": None
                }
    except Exception:
        pass

    return {
        "title": "YouTube Video",
        "text": "",
        "description": "YouTube video link provided",
        "author": None,
        "publication_date": None,
        "image_url": None,
        "video_url": url,
        "has_citations": False,
        "is_inaccessible": False,
        "platform_info": platform_info,
        "inaccessible_message": None
    }
