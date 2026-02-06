import json
import os
import sys
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from engine import CricketAnalyzer
from utils.test_recorder import SnapshotRecorder

def update_all_snapshots():
    print(f"🔄 Starting Snapshot Update...")
    
    # Fixtures dir relative to this script
    fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
    
    if not os.path.exists(fixtures_dir):
        print(f"❌ Directory not found: {fixtures_dir}")
        return

    # Initialize Engine
    print("⚙️ Initializing Engine...")
    engine = CricketAnalyzer("data/FINAL_ODI_MASTER.csv")
    recorder = SnapshotRecorder(fixtures_dir)

    for filename in os.listdir(fixtures_dir):
        if not filename.endswith(".json"):
            continue
        
        # Skip regression file (it has its own updater via run_venue_regression --merge)
        if "expected_results" in filename or "latest_test_run" in filename or "final_results" in filename:
            continue
        
        function_name = filename.replace(".json", "")
        filepath = os.path.join(fixtures_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                scenarios = json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load {filename}: {e}")
            continue
            
        if not scenarios:
            continue

        # Check legacy list format
        if not isinstance(scenarios, list):
             print(f"⚠️ Skipping {filename} (Not a list scenario file).")
             continue

        print(f"📝 Updating {function_name} ({len(scenarios)} scenarios)...")
        updated_scenarios = []
        
        func = getattr(engine, function_name, None)
        if not func:
            print(f"❌ Function '{function_name}' not found in engine. Skipping.")
            continue

        for scenario in scenarios:
            inputs = scenario["inputs"]
            
            # Helper to deserialize inputs just for execution
            def deserialize_inputs(obj):
                if isinstance(obj, dict) and obj.get('__type__') == 'pandas_dataframe':
                    return pd.DataFrame.from_dict(obj['data'], orient='split')
                if isinstance(obj, dict):
                    return {k: deserialize_inputs(v) for k, v in obj.items()}
                return obj

            run_inputs = deserialize_inputs(inputs)

            try:
                if isinstance(run_inputs, dict):
                    actual = func(**run_inputs)
                elif isinstance(run_inputs, list):
                    actual = func(*run_inputs)
                else:
                    actual = func(run_inputs)
                
                # Update output
                scenario["expected_output"] = recorder._serialize(actual)
                updated_scenarios.append(scenario)
                
            except Exception as e:
                print(f"❌ Error running scenario in {filename}: {e}")
                updated_scenarios.append(scenario)

        # Write back
        with open(filepath, 'w') as f:
            json.dump(updated_scenarios, f, indent=4)
        print(f"✅ Updated {filename}")

    print("\n✨ All snapshots updated.")

if __name__ == "__main__":
    update_all_snapshots()
