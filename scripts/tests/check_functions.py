"""Check all manifest functions and test each via the API. Output to file."""
import requests
import json
from config.settings import API_BASE_URL, API_LEGACY_PREFIX

BASE = API_BASE_URL
m = requests.get(f"{BASE}{API_LEGACY_PREFIX}/odi/manifest").json()

all_fns = []
for cat in m["categories"]:
    for fn in cat["functions"]:
        ctx = fn.get("required_context", [])
        all_fns.append((cat["key"], fn["key"], fn["output_type"], ctx))

sample_ctx = {
    "venue": "IND_MUMBAI_WANKHEDE",
    "team_a": "India",
    "team_b": "Australia",
    "years": 5,
    "region": "All",
}

results = []
for cat_id, fn_id, out_type, req_ctx in all_fns:
    try:
        r = requests.post(
            f"{BASE}{API_LEGACY_PREFIX}/odi/execute/{fn_id}",
            json={"params": sample_ctx},
            timeout=30,
        )
        if r.status_code == 200:
            data = r.json()
            result = data.get("data")
            if isinstance(result, list):
                dtype = "list"
                size = f"{len(result)} rows"
            elif isinstance(result, dict):
                dtype = "dict"
                size = f"{len(result)} keys"
            else:
                dtype = str(type(result).__name__)
                size = "-"
            status = "OK"
            notes = f"output_type={data.get('output_type', '?')}"
        else:
            status = f"FAIL-{r.status_code}"
            dtype = "-"
            size = "-"
            try:
                err = r.json()
                notes = str(err.get("detail", ""))[:120]
            except (ValueError, TypeError, KeyError, AttributeError):
                notes = r.text[:120]
    except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
        status = "ERROR"
        dtype = "-"
        size = "-"
        notes = str(e)[:120]
    
    results.append({
        "cat": cat_id,
        "fn": fn_id,
        "output_type": out_type,
        "ctx": req_ctx,
        "status": status,
        "dtype": dtype,
        "size": size,
        "notes": notes,
    })

with open("scripts/fn_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Done. {len(results)} functions tested. See scripts/fn_results.json")
