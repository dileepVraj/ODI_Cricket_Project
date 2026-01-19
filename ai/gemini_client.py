import google.generativeai as genai
import json
import os
import re

class GeminiOracle:
    def __init__(self, api_key=None):
        self.api_key = api_key if api_key else os.getenv("GEMINI_API_KEY")
        if not self.api_key or "PASTE" in self.api_key:
            print("⚠️ Warning: Gemini API Key is missing.")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash') 
                print("🤖 Gemini 2.0 Brain Connected.")
            except Exception as e:
                print(f"❌ AI Connection Failed: {e}")
                self.model = None

    def fetch_dual_team_stats(self, venue_name, players_a, players_b):
        """
        Fetches stats for BOTH teams in ONE single API call to avoid Rate Limits.
        """
        # 🚨 SAFETY NET (Indore Backup)
        safety_net = {
            "Shubman Gill": {"Ven Inns": 2, "Ven Runs": 216, "Ven Avg": 108.0, "100/50": "2/0"},
            "Shreyas Iyer": {"Ven Inns": 1, "Ven Runs": 105, "Ven Avg": 105.0, "100/50": "1/0"},
            "Devon Conway": {"Ven Inns": 1, "Ven Runs": 138, "Ven Avg": 138.0, "100/50": "1/0"},
            "Rohit Sharma": {"Ven Inns": 5, "Ven Runs": 205, "Ven Avg": 41.0,  "100/50": "1/1"},
            "KL Rahul":     {"Ven Inns": 1, "Ven Runs": 52,  "Ven Avg": 52.0,  "100/50": "0/1"},
            "Virat Kohli":  {"Ven Inns": 4, "Ven Runs": 99,  "Ven Avg": 33.0,  "100/50": "0/0"},
            "Hardik Pandya": {"Ven Inns": 2, "Ven Runs": 132, "Ven Avg": 66.0, "100/50": "0/2"},
            "Mitchell Santner": {"Ven Inns": 1, "Ven Runs": 34, "Ven Avg": 34.0, "100/50": "0/0"},
            "Daryl Mitchell": {"Ven Inns": 1, "Ven Runs": 24, "Ven Avg": 24.0, "100/50": "0/0"}
        }

        if not self.model: 
            return safety_net if "Indore" in venue_name or "IND_INDORE" in venue_name else {}
        
        # 🤖 THE UNIFIED REQUEST
        list_a = ", ".join(players_a)
        list_b = ", ".join(players_b)
        
        print(f"🤖 AI Researching {len(players_a) + len(players_b)} players at {venue_name} (One Call)...")
        
        prompt = f"""
        Act as a Cricket Statistician.
        I need ODI batting records for these players at "{venue_name}".
        
        Group A: {list_a}
        Group B: {list_b}
        
        Task:
        1. Identify players who have played ODI matches at this venue.
        2. Extract their Runs, Avg, and Centuries.
        3. IGNORE players with 0 matches.
        
        Return ONE JSON object with player names as keys:
        {{
            "Shubman Gill": {{ "Ven Inns": 2, "Ven Runs": 216, "Ven Avg": 108.0, "100/50": "2/0" }},
            "Player Name": {{ "Ven Inns": int, "Ven Runs": int, "Ven Avg": float, "100/50": "string" }}
        }}
        JSON ONLY.
        """
        
        try:
            response = self.model.generate_content(prompt)
            clean_text = re.sub(r'```json\n|\n```|```', '', response.text).strip()
            data = json.loads(clean_text)
            
            if not data:
                raise ValueError("Empty Data")
                
            print(f"✅ AI Success! Retrieved data for {len(data)} players.")
            return data
            
        except Exception as e:
            print(f"⚠️ AI Busy/Failed ({e}). Using Safety Net.")
            if "IND_INDORE" in venue_name or "Indore" in venue_name:
                return safety_net
            return {}