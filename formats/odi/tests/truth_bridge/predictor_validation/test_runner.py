from formats.odi.tests.truth_bridge.base_runner import TruthBridgeBase
from config.shared.venues import VENUE_MAP
import sys

class PredictorValidationRunner(TruthBridgeBase):
    def run_tests(self):
        print(f"\n🔮 [{self.suite_name}] Initializing Predictor Logic Check...")
        
        # Test Cases: Diverse conditions to stress-test the new Vectorized Engine
        scenarios = [
            # Case 1: High Scoring Venue (Indore)
            ("India", ["RG Sharma", "V Kohli", "Shubman Gill"], "Australia", ["MA Starc", "PJ Cummins", "A Zampa"], "Holkar Cricket Stadium, Indore", 5),
            
            # Case 2: Low Scoring/Spin Friendly (Chennai)
            ("Australia", ["TM Head", "SPD Smith", "M Labuschagne"], "India", ["JJ Bumrah", "Kuldeep Yadav", "RA Jadeja"], "MA Chidambaram Stadium, Chepauk, Chennai", 5),
            
            # Case 3: Neutral/Pace (Lord's)
            ("England", ["JE Root", "JC Buttler", "BA Stokes"], "New Zealand", ["TA Boult", "TG Southee", "MJ Santner"], "Lord's, London", 5)
        ]

        for i, (bat_team, bat_players, bowl_team, bowl_players, venue, years) in enumerate(scenarios, 1):
            key_path = [f"Scenario_{i}", f"{bat_team}_vs_{bowl_team}", venue]
            print(f"\n[Case {i}] Predict {bat_team} vs {bowl_team} at {venue} ({years}y)...")
            
            try:
                # RUN ENGINE
                packet = self.analyzer.predictor_engine.predict_score(
                    batting_team=bat_team,
                    batting_players=bat_players,
                    bowling_team=bowl_team,
                    bowling_players=bowl_players,
                    venue_id=venue,
                    years=years
                )
                
                # EXTRACT KEY METRICS
                fingerprint = {
                    "Venue_Avg": packet['venue_avg'],
                    "Bat_Factor": packet['bat_factor'],
                    "Bowl_Factor": packet['bowl_factor'],
                    "Prediction_Lower": packet['lower'],
                    "Prediction_Upper": packet['upper'],
                    "Risk_Labels": packet['adjustment_msg']
                }

                # COMPARE WITH TRUTH
                expected = self.ground_truth.get(self.suite_name, {}).get(" > ".join(key_path))
                
                if expected:
                    self.compare(key_path, fingerprint, expected)
                else:
                    # SEED MODE
                    print(f"      🌱 New Scenario Detected. Seeding Ground Truth...")
                    self.ground_truth.setdefault(self.suite_name, {})[" > ".join(key_path)] = fingerprint

            except Exception as e:
                print(f"      🔴 [CRASH] {e}")
                self.results["failures"].append({"item": str(key_path), "status": "CRASH", "error": str(e)})
                self.results["summary"]["fail"] += 1

if __name__ == "__main__":
    import os
    runner = PredictorValidationRunner("PredictorValidation", "formats/odi/tests/truth_bridge/predictor_validation/ground_truth.json")
    
    # SEED MODE TRIGGER
    if len(sys.argv) > 1 and sys.argv[1] == "--seed":
        import os
        os.environ["SEED_MODE"] = "1"
    
    runner.run_tests()
    
    if os.environ.get("SEED_MODE") == "1":
        runner.save_seeded_truth()
    else:
        runner.save_report("formats/odi/tests/truth_bridge/predictor_validation/report.json")
