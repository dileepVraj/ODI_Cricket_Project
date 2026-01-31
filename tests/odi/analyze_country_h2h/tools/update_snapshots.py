import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from tests.odi.analyze_country_h2h.tools.run_h2h_regression import generate_data, merge_results

def update_snapshots():
    print("🔄 Updating Country H2H Snapshots...")
    generate_data()
    merge_results()
    print("✅ Snapshots updated.")

if __name__ == "__main__":
    update_snapshots()
