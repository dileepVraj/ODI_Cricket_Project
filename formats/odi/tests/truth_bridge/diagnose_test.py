from formats.odi.tests.truth_bridge.base_runner import TruthBridgeBase

class MockRunner(TruthBridgeBase):
    def __init__(self):
        # Bypass file loading
        self.results = {"summary": {"pass": 0, "fail": 0}, "failures": [], "details": []}

print("🧪 Testing Diagnosis Logic...")
runner = MockRunner()

# Case 1: Logic Regression (IDs match, Value differs)
print("\n--- Case 1: Logic Regression ---")
truth = {"Metric": "Avg", "Value": 50, "MATCH_IDS": "1,2,3"}
engine = {"Metric": "Avg", "Value": 45, "MATCH_IDS": "1,2,3"} # IDs match
runner.compare(["TestWithList"], [engine], [truth])

# Case 2: Data Drift (Engine has EXTRA ID)
print("\n--- Case 2: Data Drift ---")
truth_drift = {"Metric": "Avg", "Value": 50, "MATCH_IDS": "1,2,3"}
engine_drift = {"Metric": "Avg", "Value": 52, "MATCH_IDS": "1,2,3,4"} # ID 4 is new
runner.compare(["TestDrift"], [engine_drift], [truth_drift])

# Case 3: Filtering Regression (Engine MISSING ID)
print("\n--- Case 3: Filtering Regression ---")
truth_filter = {"Metric": "Avg", "Value": 50, "MATCH_IDS": "1,2,3"}
engine_filter = {"Metric": "Avg", "Value": 48, "MATCH_IDS": "1,2"} # ID 3 is missing
runner.compare(["TestFilter"], [engine_filter], [truth_filter])
