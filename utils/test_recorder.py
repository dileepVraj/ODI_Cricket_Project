import json
import os
import pandas as pd
import numpy as np

class SnapshotRecorder:
    def __init__(self, base_path="tests/fixtures"):
        self.base_path = base_path

    def _serialize(self, obj):
        """Recursively convert objects (DataFrames, Series, ndarrays) to JSON-serializable formats."""
        if isinstance(obj, pd.DataFrame):
            return {
                '__type__': 'pandas_dataframe',
                'data': obj.to_dict(orient='split')
            }
        elif isinstance(obj, pd.Series):
            return {
                '__type__': 'pandas_series',
                'data': obj.to_dict()
            }
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize(i) for i in obj]
        return obj

    def save_snapshot(self, format_name, function_name, inputs, output, description):
        """
        Saves a test snapshot to tests/fixtures/{format_name}/{function_name}.json
        """
        # Ensure directory exists
        dir_path = os.path.join(self.base_path, format_name)
        os.makedirs(dir_path, exist_ok=True)
        
        file_path = os.path.join(dir_path, f"{function_name}.json")
        
        # Load existing scenarios
        scenarios = []
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    scenarios = json.load(f)
            except json.JSONDecodeError:
                scenarios = []

        # Create new scenario (inputs are assumed to be JSON serializable or need similar processing if complex)
        # We might need to serialize inputs too if they contain complex types, but usually they are simple args.
        # Ideally, we should serialize inputs as well to be safe.
        
        new_scenario = {
            "description": description,
            "inputs": self._serialize(inputs),
            "expected_output": self._serialize(output)
        }
        
        scenarios.append(new_scenario)
        
        # Write back
        with open(file_path, 'w') as f:
            json.dump(scenarios, f, indent=4)
        
        print(f"✅ Snapshot saved to {file_path}")

