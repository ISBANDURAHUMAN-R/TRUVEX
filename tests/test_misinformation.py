import sys
from pathlib import Path

# Fix Windows console emoji encoding
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_misinformation_detection():
    print("Testing viral misinformation claim: 'Lemon and baking soda cures all cancer'...")
    payload = {
        "text": "Drinking hot water with lemon and baking soda cures 100% of all cancer in 48 hours and is 10,000 times stronger than chemotherapy. Doctors are hiding this."
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    print(f"  -> Overall Verdict: {data['overall_verdict']}")
    print(f"  -> Trust Score: {data['trust_score']}/100")
    print(f"  -> Misinformation Type: {data['misinformation_type']}")
    print(f"  -> Claims extracted: {len(data['claims'])}")
    
    # Must be either FALSE or MISLEADING or UNVERIFIED with low trust score
    assert data["trust_score"] < 65, f"Trust score unexpectedly high: {data['trust_score']}"
    assert "TRUE" not in data["verdict_badge"] or "MOSTLY" in data["verdict_badge"], "Falsely classified as completely true!"
    
    print("  -> Passed: Misinformation claim correctly assigned low trust and flagged.")

if __name__ == "__main__":
    test_misinformation_detection()
