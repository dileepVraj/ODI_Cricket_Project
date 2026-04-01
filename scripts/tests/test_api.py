"""Quick API smoke test — validates all endpoints."""
import requests
import json
import sys
from config.settings import API_BASE_URL, API_V1_PREFIX

BASE = API_BASE_URL

def test(name, url, method="GET", body=None, expected_status=200):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"  {method} {url}")
    try:
        if method == "GET":
            r = requests.get(url, timeout=10)
        else:
            r = requests.post(url, json=body, timeout=30)
        
        print(f"  STATUS: {r.status_code}")
        data = r.json()
        
        # Print compact version
        text = json.dumps(data, indent=2, ensure_ascii=False)
        if len(text) > 500:
            print(f"  RESPONSE (truncated):\n{text[:500]}...")
        else:
            print(f"  RESPONSE:\n{text}")
        
        if r.status_code == expected_status:
            print("  ✅ PASSED")
        else:
            print(f"  ❌ FAILED (expected {expected_status})")
        return r.status_code, data
    except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
        print(f"  ❌ ERROR: {e}")
        return 0, None

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

print("🏏 Cricket API Smoke Test")
print("=" * 60)

# 1. Health
test("Health Check", f"{BASE}/health")

# 2. Formats
test("Format Discovery", f"{BASE}{API_V1_PREFIX}/formats")

# 3. Manifest
code, data = test("ODI Manifest", f"{BASE}{API_V1_PREFIX}/odi/manifest")
if data:
    cats = len(data.get("categories", []))
    fns = sum(len(c.get("functions", [])) for c in data.get("categories", []))
    print(f"  📊 {cats} categories, {fns} functions")

# 4. Context: Teams
code, data = test("Teams List", f"{BASE}{API_V1_PREFIX}/odi/context/teams")
if data:
    print(f"  🏏 {len(data.get('teams', []))} teams")

# 5. Context: Venues
code, data = test("Venues List", f"{BASE}{API_V1_PREFIX}/odi/context/venues")
if data:
    print(f"  🏟️ {len(data.get('venues', []))} venues")

# 6. Context: Players (India)
code, data = test("Players (India)", f"{BASE}{API_V1_PREFIX}/odi/context/players/India")
if data:
    print(f"  👤 {len(data.get('players', []))} players")

# 7. Context: Regions
test("Regions", f"{BASE}{API_V1_PREFIX}/odi/context/regions")

# 8. Execute: venue_bias
test("Execute: venue_bias", f"{BASE}{API_V1_PREFIX}/odi/execute/venue_bias", "POST", {
    "params": {"venue": "IND_MUMBAI_WANKHEDE", "years": 5}
})

# 9. Execute: global_h2h
test("Execute: global_h2h", f"{BASE}{API_V1_PREFIX}/odi/execute/global_h2h", "POST", {
    "params": {"team_a": "India", "team_b": "Australia", "years": 5}
})

# 10. Execute: team_form
test("Execute: team_form", f"{BASE}{API_V1_PREFIX}/odi/execute/team_form", "POST", {
    "params": {"team_a": "India", "years": 3}
})

# 11. Error: bad format (EXPECTED 404)
test("Error: Bad format (expect 404)", f"{BASE}{API_V1_PREFIX}/xyz/manifest", expected_status=404)

# 12. Error: bad function key (EXPECTED 404)
test("Error: Bad function (expect 404)", f"{BASE}{API_V1_PREFIX}/odi/execute/nonexistent", "POST", {
    "params": {}
}, expected_status=404)

print("\n" + "=" * 60)
print("🏁 SMOKE TEST COMPLETE")
print("=" * 60)
