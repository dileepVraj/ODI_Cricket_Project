import sys
import os
sys.path.append(os.getcwd())

from formats.odi.tests.truth_bridge.base_runner import TruthBridgeBase

class TeamFormValidationRunner(TruthBridgeBase):
    def run_tests(self):
        print(f"\n🦁 [{self.suite_name}] Initializing Team Form Check...")
        
        # Test Scenarios
        # (Team, Opponent, Continent, Limit)
        scenarios = [
            ("India", "All", "All", 5),      # Global recent form
            ("Australia", "India", "All", 5), # Specific Opponent
            ("England", "All", "Asia", 5),    # Specific Continent
            ("South Africa", "Australia", "Oceania", 5) # Specific Opponent in Continent
        ]

        for i, (team, opp, cont, limit) in enumerate(scenarios, 1):
            key_path = [f"Scenario_{i}", team, f"vs_{opp}", f"in_{cont}"]
            item_label = " > ".join(key_path)
            print(f"\n[Case {i}] Analyzing {item_label}...")
            
            try:
                # RUN ENGINE
                form_data = self.analyzer.team_engine.analyze_team_form(
                    team_name=team,
                    opp_team=opp,
                    continent=cont,
                    limit=limit
                )
                
                # EXTRACT KEY METRICS (Fingerprint)
                # form_data is a list of dicts.
                # We want to capture the sequence of results and scores.
                fingerprint = []
                for match in form_data:
                    fingerprint.append({
                        "Date": match.get("Date"),
                        "Opponent": match.get("Opponent"),
                        "Result": match.get("Result"),
                        "Score": match.get("TeamScore"),
                        "OppScore": match.get("OppScore")
                    })

                # COMPARE WITH TRUTH
                expected = self.ground_truth.get(self.suite_name, {}).get(item_label)
                
                if expected:
                    self.compare(key_path, fingerprint, expected)
                else:
                    # SEED MODE
                    print("      🌱 New Scenario Detected. Seeding Ground Truth...")
                    self.ground_truth.setdefault(self.suite_name, {})[item_label] = fingerprint

            except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
                print(f"      🔴 [CRASH] {e}")
                self.results["failures"].append({"item": item_label, "status": "CRASH", "error": str(e)})
                self.results["summary"]["fail"] += 1

if __name__ == "__main__":
    import os
    runner = TeamFormValidationRunner("TeamFormValidation", "formats/odi/tests/truth_bridge/team_form_validation/ground_truth.json")
    
    # SEED MODE TRIGGER
    if len(sys.argv) > 1 and sys.argv[1] == "--seed":
        os.environ["SEED_MODE"] = "1"
    
    runner.run_tests()
    
    if os.environ.get("SEED_MODE") == "1":
        runner.save_seeded_truth()
    else:
        runner.save_report("formats/odi/tests/truth_bridge/team_form_validation/report.json")
