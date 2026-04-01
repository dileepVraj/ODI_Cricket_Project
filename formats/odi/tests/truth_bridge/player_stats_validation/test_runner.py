import sys
import os
sys.path.append(os.getcwd())

from formats.odi.tests.truth_bridge.base_runner import TruthBridgeBase
from dataclasses import asdict

class PlayerStatsValidationRunner(TruthBridgeBase):
    def run_tests(self):
        print(f"\n🏏 [{self.suite_name}] Initializing Player Stats Check...")
        
        # Test Scenarios
        # (Player Name, Opposition, Venue ID, Years)
        scenarios = [
            ("V Kohli", None, None, 10),  # Overall
            ("RG Sharma", "Australia", None, 5),  # Vs Opponent
            ("JJ Bumrah", None, "IND_MUMBAI_WANKHEDE", 5),  # At Venue
            ("V Kohli", "Pakistan", "ENG_LONDON_LORDS", 20), # Specific matchup 
            ("MA Starc", None, None, 5) # Bowler Overall
        ]

        for i, (player, opp, venue, years) in enumerate(scenarios, 1):
            key_parts = [f"Scenario_{i}", player]
            if opp:
                key_parts.append(f"vs_{opp}")
            if venue:
                key_parts.append(f"at_{venue}")
            
            key_path = key_parts
            item_label = " > ".join(key_path)
            print(f"\n[Case {i}] Analyzing {item_label} ({years}y)...")
            
            try:
                # RUN ENGINE
                # Note: creating a separate 'analyze_player_profile' interface in the runner might be cleaner
                # but accessing engine directly is fine for truth bridge.
                profile = self.analyzer.player_engine.get_player_profile(
                    player_name=player,
                    opposition=opp,
                    venue_id=venue,
                    years=years
                )
                
                # EXTRACT KEY METRICS (Fingerprint)
                # Convert dataclass to dict and flatten relevant parts
                data = asdict(profile)
                
                fingerprint = {}
                
                # Batting Stats
                if data.get('batting'):
                    fingerprint['Bat_Inns'] = data['batting']['innings']
                    fingerprint['Bat_Runs'] = data['batting']['runs']
                    fingerprint['Bat_Avg'] = data['batting']['average']
                    fingerprint['Bat_SR'] = data['batting']['strike_rate']
                
                # Bowling Stats
                if data.get('bowling'):
                    fingerprint['Bowl_Inns'] = data['bowling']['innings']
                    fingerprint['Bowl_Wkts'] = data['bowling']['wickets']
                    fingerprint['Bowl_Avg'] = data['bowling']['average']
                    fingerprint['Bowl_Econ'] = data['bowling']['economy']

                # Context Stats (Venue/Opponent specific if applicable)
                if venue and data.get('venue_stats'):
                     if data['venue_stats'].get('batting'):
                        fingerprint['Venue_Bat_Runs'] = data['venue_stats']['batting']['runs']
                        fingerprint['Venue_Bat_Avg'] = data['venue_stats']['batting']['average']
                
                if opp and data.get('vs_opponent_stats'):
                     if data['vs_opponent_stats'].get('batting'):
                        fingerprint['Opp_Bat_Runs'] = data['vs_opponent_stats']['batting']['runs']
                        fingerprint['Opp_Bat_Avg'] = data['vs_opponent_stats']['batting']['average']

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
    runner = PlayerStatsValidationRunner("PlayerStatsValidation", "formats/odi/tests/truth_bridge/player_stats_validation/ground_truth.json")
    
    # SEED MODE TRIGGER
    if len(sys.argv) > 1 and sys.argv[1] == "--seed":
        os.environ["SEED_MODE"] = "1"
    
    runner.run_tests()
    
    if os.environ.get("SEED_MODE") == "1":
        runner.save_seeded_truth()
    else:
        runner.save_report("formats/odi/tests/truth_bridge/player_stats_validation/report.json")
