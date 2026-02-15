from fastapi.testclient import TestClient
from api.main import app
import sys
import os

# Ensure we can import from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Ensure we can import from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    # Use context manager to trigger startup/shutdown events (loading the engine)
    with TestClient(app) as client:
        print("\n🔵 TESTING HEALTH ENDPOINT...")
        try:
            response = client.get("/health")
            assert response.status_code == 200
            json_data = response.json()
            print(f"✅ Health Check Passed: {json_data}")
        except AssertionError:
            print(f"❌ Health Check Failed: {response.text}")
        except Exception as e:
            print(f"🔥 Exception in Health Check: {e}")

        print("\n🔵 TESTING PREDICTION ENDPOINT...")
        payload = {
            "batting_team": "India",
            "batting_players": ["Virat Kohli", "Rohit Sharma"],
            "bowling_team": "Australia",
            "bowling_players": ["Mitchell Starc", "Pat Cummins"],
            "venue_id": "Wankhede Stadium, Mumbai",
            "years": 5
        }
        
        try:
            response = client.post("/predict", json=payload)
            if response.status_code == 200:
                print("✅ /predict Success")
                # Print concise summary to avoid massive log
                data = response.json()
                print(f"   Projected Score: {data.get('lower')} - {data.get('upper')}")
                print(f"   Verdict: {data.get('bf_text')}")
            else:
                print(f"❌ /predict Failed: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"🔥 Exception in Predict: {e}")

if __name__ == "__main__":
    run_tests()
