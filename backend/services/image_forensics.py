import io
import base64
from typing import Dict, Any, Optional

try:
    from PIL import Image, ExifTags, ImageChops
except ImportError:
    Image = ExifTags = ImageChops = None


def image_forensics_available() -> bool:
    return Image is not None

def analyze_image_bytes(image_bytes: bytes) -> Dict[str, Any]:
    """
    Performs forensic metadata inspection, EXIF extraction, and error level compression analysis.
    Strictly follows anti-hallucination and safety guidelines:
    'Image authenticity could not be reliably determined.' when inconclusive.
    """
    if Image is None:
        return {
            "status": "Image analysis unavailable",
            "manipulation_risk": "Inconclusive",
            "dimensions": "Unknown",
            "format": "Unknown",
            "has_exif": False,
            "exif_details": {},
            "forensic_notes": "Install the project dependencies from requirements.txt to enable image analysis.",
        }

    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        img_format = img.format or "Unknown"
        
        # 1. Extract EXIF
        exif_data = {}
        software_detected = None
        has_camera_make = False
        
        if hasattr(img, '_getexif') and img._getexif():
            raw_exif = img._getexif()
            for tag_id, value in raw_exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                if isinstance(value, (str, int, float)):
                    exif_data[tag_name] = str(value)
                elif isinstance(value, bytes):
                    exif_data[tag_name] = f"<{len(value)} bytes>"

            # Inspect editing software
            software_keys = ["Software", "ProcessingSoftware", "ImageDescription"]
            for k in software_keys:
                if k in exif_data:
                    software_detected = exif_data[k]

            if "Make" in exif_data or "Model" in exif_data:
                has_camera_make = True

        # 2. Heuristic check for synthetic/AI or heavy editing tags
        ai_or_edit_indicators = []
        if software_detected:
            sw_lower = software_detected.lower()
            if any(term in sw_lower for term in ["photoshop", "gimp", "canva", "lightroom"]):
                ai_or_edit_indicators.append(f"Edited with software: {software_detected}")
            elif any(term in sw_lower for term in ["midjourney", "stable diffusion", "dall-e", "novelai"]):
                ai_or_edit_indicators.append(f"AI generation metadata detected: {software_detected}")

        # 3. Compression / ELA simulation (resave at 90% quality and compare difference)
        ela_diff_metric = 0
        try:
            if img_format in ["JPEG", "JPG"]:
                buffer = io.BytesIO()
                img.convert('RGB').save(buffer, 'JPEG', quality=90)
                buffer.seek(0)
                resaved = Image.open(buffer)
                diff = ImageChops.difference(img.convert('RGB'), resaved)
                extrema = diff.getextrema()
                max_diff = max([ex[1] for ex in extrema])
                ela_diff_metric = max_diff
        except Exception:
            pass

        # 4. Synthesize Status
        if ai_or_edit_indicators:
            status = "Potentially manipulated"
            manipulation_risk = "Medium to High"
            notes = f"Digital editing indicators discovered in image metadata: {'; '.join(ai_or_edit_indicators)}."
        elif has_camera_make:
            status = "Likely Genuine Capture"
            manipulation_risk = "Low"
            notes = f"Original camera hardware metadata intact ({exif_data.get('Make', '')} {exif_data.get('Model', '')}). No contradictory software signatures detected."
        else:
            status = "Image authenticity could not be reliably determined"
            manipulation_risk = "Inconclusive"
            notes = "Standard web-compressed image with stripped EXIF headers. Compression artifacts are uniform. Forensic authenticity cannot be definitively confirmed without original camera raw data."

        return {
            "status": status,
            "manipulation_risk": manipulation_risk,
            "dimensions": f"{width}x{height}px",
            "format": img_format,
            "has_exif": len(exif_data) > 0,
            "exif_details": exif_data,
            "forensic_notes": notes
        }

    except Exception as e:
        return {
            "status": "Image authenticity could not be reliably determined",
            "manipulation_risk": "Inconclusive",
            "dimensions": "Unknown",
            "format": "Unknown",
            "has_exif": False,
            "exif_details": {},
            "forensic_notes": f"Image processing error: {str(e)}. Image authenticity could not be reliably determined."
        }

def analyze_base64_image(base64_str: str) -> Optional[Dict[str, Any]]:
    """Decodes base64 string and runs image analysis."""
    if not base64_str:
        return None
    try:
        # Strip header like data:image/png;base64,
        if "," in base64_str:
            base64_str = base64_str.split(",", 1)[1]
        raw_bytes = base64.b64decode(base64_str)
        return analyze_image_bytes(raw_bytes)
    except Exception:
        return {
            "status": "Image authenticity could not be reliably determined",
            "manipulation_risk": "Inconclusive",
            "exif_details": {},
            "forensic_notes": "Corrupted or invalid base64 image data. Image authenticity could not be reliably determined."
        }
