import requests
import json
from config.settings import API_BASE_URL, API_V1_PREFIX

URL = f"{API_BASE_URL}{API_V1_PREFIX}/odi/execute/predict_score"
payload = {
    "params": {
        "team_a": "India",
        "team_b": "Australia",
        "venue": "Holkar Cricket Stadium, Indore",
        "years": 5,
        "home_xi": ["RG Sharma", "Shubman Gill", "V Kohli", "SS Iyer", "KL Rahul", "SA Yadav", "RA Jadeja", "R Ashwin", "SN Thakur", "Mohammed Shami", "Mohammed Siraj"],
        "away_xi": ["DA Warner", "MR Marsh", "MS Wade", "M Labuschagne", "C Green", "MP Stoinis", "MW Short", "PJ Cummins", "AL Zampa", "JR Hazlewood", "SA Abbott"]
    }
}

resp = requests.post(URL, json=payload)
print(json.dumps(resp.json(), indent=2))
