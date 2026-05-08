import os
import sys
import json
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../..")))  # noqa: E402

# 🚷 HEADLESS MOCK: Prevent IPython/Jupyter overhead in Truth Bridge
import builtins
def mock_display(*args, **kwargs): pass
builtins.display = mock_display  # type: ignore[attr-defined]
builtins.HTML = lambda x: x  # type: ignore[attr-defined]

from formats.odi.tests.truth_bridge.base_runner import TruthBridgeBase  # noqa: E402

class CompareSquadsTruthBridge(TruthBridgeBase):
    def __init__(self):
        truth_path = os.path.join(os.path.dirname(__file__), 'ground_truth.json')
        super().__init__("Compare Squads", truth_path)
        
        # 🩹 FIX: Base runner initializes a skeleton we don't want for this specific schema
        if "Compare Squads" in self.ground_truth:
             del self.ground_truth["Compare Squads"]

        print("⚖️ Initializing Compare Squads Truth Bridge (v2.5)")
        
        # Paths to legacy fixture for bootstrapping
        self.legacy_fixture_path = os.path.join(
            os.path.dirname(__file__), 
            "../../regression_suite/compare_squads/fixtures/compare_squads_expected_results.json"
        )

    def _load_legacy_scenarios(self):
        """Loads scenarios from the legacy fixture if ground truth is empty."""
        try:
            with open(self.legacy_fixture_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (OSError, ValueError, KeyError, TypeError) as e:
            print(f"⚠️ Could not load legacy scenarios: {e}")
            return {}

    def run(self):
        SEED_MODE = os.environ.get("SEED_MODE") == "1"
        
        # 1. Determine Scenario Space
        print(f"DEBUG: Initial ground_truth keys: {list(self.ground_truth.keys())}")
        if SEED_MODE and not self.ground_truth:
            print("🆕 Bootstrapping from Legacy Scenarios...")
            scenarios = self._load_legacy_scenarios()
            print(f"DEBUG: Loaded {len(scenarios)} scenarios from legacy.")
        else:
            scenarios = self.ground_truth
            print(f"DEBUG: Using {len(scenarios)} scenarios from current ground_truth.")

        if not scenarios:
            print(f"❌ No scenarios found to run. SEED_MODE={SEED_MODE}, ground_truth_empty={not self.ground_truth}")
            return

        total_scenarios = len(scenarios)
        print(f"🔎 Scanning {total_scenarios} matchups across 3 analytical layers.")

        for idx, (scenario_key, scenario_data) in enumerate(scenarios.items()):
            print(f"[{idx+1}/{total_scenarios}] ⚖️ Processing Matchup: {scenario_key}")
            
            meta = scenario_data.get('Meta')
            if not meta:
                print(f"      ⚠️ Skipping {scenario_key}: Missing Meta.")
                continue

            home_team = scenario_key.split("_vs_")[0]
            away_team = scenario_key.split("_vs_")[1]
            
            try:
                context_df = pd.DataFrame()
                dal = getattr(self.analyzer, "dal", None)
                if dal is not None:
                    players = sorted(set(meta['HomeXI'] + meta['AwayXI']))
                    context_df = dal.get_balls(players=players)
                    if not context_df.empty and 'start_date' in context_df.columns:
                        context_df = context_df.copy()
                        context_df['start_date'] = pd.to_datetime(context_df['start_date'], errors='coerce')
                        max_date = context_df['start_date'].max()
                        if pd.notna(max_date):
                            cutoff_date = pd.Timestamp(max_date).floor('D') - pd.DateOffset(years=int(meta['Years']))
                        else:
                            cutoff_date = pd.Timestamp.now().floor('D') - pd.DateOffset(years=int(meta['Years']))
                        context_df = context_df[context_df['start_date'] >= cutoff_date]

                # _generate_comparison_payload(self, team_a_name, team_a_players, team_b_name, team_b_players, venue_id, years=None)
                engine_data = self.analyzer.player_engine._generate_comparison_payload(
                    home_team, meta['HomeXI'], 
                    away_team, meta['AwayXI'], 
                    meta['Venue'], 
                    years=meta['Years'],
                    context_df=context_df,
                )
            except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
                print(f"      ❌ [ERROR] Engine failed for {scenario_key}: {e}")
                continue

            if SEED_MODE:
                self.ground_truth[scenario_key] = {
                    "Meta": meta,
                    "Payload": engine_data
                }
                continue

            truth_payload = scenario_data.get('Payload')
            if not truth_payload:
                print(f"      ⚠️ Missing ground truth payload for {scenario_key}. Run in SEED_MODE.")
                continue

            # Section-based Comparison using Truth Bridge base
            # 1. SquadSummary (Flattened)
            for team in [home_team, away_team]:
                self.compare([scenario_key, "SquadMetrics", team], 
                             engine_data.get('SquadComparison', {}).get(team), 
                             truth_payload.get('SquadComparison', {}).get(team))
            
            # 2. TacticalMatrix (Row-by-Row)
            for team in [home_team, away_team]:
                e_matrix = engine_data.get('TacticalMatrix', {}).get(team, [])
                t_matrix = truth_payload.get('TacticalMatrix', {}).get(team, [])
                
                # Compare each player row individually as a dict
                for i, e_row in enumerate(e_matrix):
                    if i < len(t_matrix):
                         self.compare([scenario_key, "Tactical", team, e_row.get('Player')], e_row, t_matrix[i])

            # 3. Matchups (Player-by-Player)
            for team in [home_team, away_team]:
                e_matchups = engine_data.get('Matchups', {}).get(team, {})
                t_matchups = truth_payload.get('Matchups', {}).get(team, {})
                for player, e_data in e_matchups.items():
                    if player in t_matchups:
                         self.compare([scenario_key, "Matchups", team, player], e_data, t_matchups[player])
            
            # 4. Fingerprint (MATCH_IDS)
            self.compare([scenario_key, "Fingerprint"], {"MATCH_IDS": engine_data.get('MATCH_IDS')}, {"MATCH_IDS": truth_payload.get('MATCH_IDS')})

        if SEED_MODE:
            self.save_seeded_truth()
        else:
            self.save_report(os.path.join(os.path.dirname(__file__), 'report.json'))

if __name__ == "__main__":
    runner = CompareSquadsTruthBridge()
    runner.run()
