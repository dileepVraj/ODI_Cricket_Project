import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from tests.odi.analyze_home_fortress.tools.run_fortress_regression import generate_data, merge_results

def update_snapshots():
    print("🔄 Updating Fortress Snapshots...")
    # Leveraging the regression script's logic
    generate_data()
    merge_results()
    print("✅ Snapshots updated.")

if __name__ == "__main__":
    update_snapshots()
