import asyncio
import sys
from pathlib import Path

# Fix Windows console emoji encoding
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_status_endpoint():
    print("Testing GET /api/status...")
    response = client.get("/api/status")
    assert response.status_code == 200, f"Status code: {response.status_code}"
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "TruVex AI Engine"
    print("  -> Passed: System is online.")

def test_demos_endpoint():
    print("Testing GET /api/demos...")
    response = client.get("/api/demos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    print(f"  -> Passed: {len(data)} demo presets retrieved.")

def test_restricted_platform_handling():
    print("Testing restricted platform handling (Instagram URL without fallback text)...")
    payload = {
        "url": "https://www.instagram.com/p/C_abc12345/"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "Instagram"
    assert data["is_inaccessible_platform"] is True
    assert "Content could not be directly retrieved" in data["inaccessible_message"]
    assert data["overall_verdict"] == "⚪ UNVERIFIED"
    print("  -> Passed: Inaccessible platform handled gracefully with user guidance.")

def test_live_fact_check_analysis():
    print("Testing live analysis on factual NASA topic...")
    payload = {
        "text": "NASA's James Webb Space Telescope detected water vapor in the inner disk of the planetary system PDS 70.",
        "url": "https://www.nasa.gov/news-release/webb-finds-water-vapor-in-rocky-planet-forming-zone/"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200, f"Error: {response.text}"
    data = response.json()
    
    assert "id" in data
    assert len(data["claims"]) > 0
    assert "overall_verdict" in data
    assert 0 <= data["trust_score"] <= 100
    assert 0 <= data["confidence"] <= 100
    assert "source_credibility" in data
    assert "source_graph" in data
    assert len(data["source_graph"]["nodes"]) > 0
    assert "timeline_check" in data
    
    # Check that any evidence contains real URLs
    for claim in data["claims"]:
        for ev in claim["supporting_evidence"] + claim["contradicting_evidence"]:
            assert ev["link"].startswith("http"), f"Invalid link: {ev['link']}"
            assert len(ev["source_name"]) > 0
            
    print(f"  -> Passed: Factual claim verified. Verdict: {data['overall_verdict']}, Trust Score: {data['trust_score']}/100, Claims: {len(data['claims'])}")
    return data["id"]

def test_history_persistence(analysis_id=None):
    print("Testing history persistence and retrieval...")
    response = client.get("/api/history")
    assert response.status_code == 200
    history = response.json()
    if analysis_id:
        assert any(item["id"] == analysis_id for item in history)
        detail_res = client.get(f"/api/history/{analysis_id}")
        assert detail_res.status_code == 200
        detail_data = detail_res.json()
        assert detail_data["id"] == analysis_id
        print("  -> Passed: Analysis persisted in SQLite and verified in history.")
    else:
        assert isinstance(history, list)
        print(f"  -> Passed: History endpoint responded with {len(history)} items.")

if __name__ == "__main__":
    print("==================================================")
    print("  RUNNING TRUVEX AI VERIFICATION SUITE")
    print("==================================================")
    test_status_endpoint()
    test_demos_endpoint()
    test_restricted_platform_handling()
    aid = test_live_fact_check_analysis()
    test_history_persistence(aid)
    print("==================================================")
    print("  ALL TESTS PASSED SUCCESSFULLY!")
    print("==================================================")
