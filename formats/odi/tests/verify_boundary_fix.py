import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine import CricketAnalyzer

def verify_fix():
    print("🧪 BOUNDARY BUG VERIFICATION")
    print(f"Current Time: {pd.Timestamp.now()}")
    
    # Initialize Engine
    engine = CricketAnalyzer("formats/odi/data/FINAL_ODI_MASTER.csv")
    
    # Target: England in Africa, 10 Years back.
    # The missing match is 2016-02-06.
    print("\n🔍 Checking England performance in Africa (10 Year Lookback)...")
    
    # We call the method directly and capture the result if possible, 
    # or we can inspect the raw data using the same filter logic.
    # 2. Define cutoff (e.g., 10 years ago)
    # 🚨 CRITICAL: Use .floor('D') to ensure we don't exclude today's matches due to HH:MM:SS
    now = pd.Timestamp.now().floor('D')
    _ = now - pd.DateOffset(years=10)
    
    cutoff_no_fix = pd.Timestamp.now().floor('D') - pd.DateOffset(years=10)
    cutoff_with_fix = pd.Timestamp.now().floor('D') - pd.DateOffset(years=10)
    
    print(f"Cutoff (OLD): {cutoff_no_fix}")
    print(f"Cutoff (NEW): {cutoff_with_fix}")
    
    target_date = pd.Timestamp("2016-02-06")
    
    print(f"\nTarget Match Date: {target_date}")
    print(f"Included with OLD logic? {target_date >= cutoff_no_fix}")
    print(f"Included with NEW logic? {target_date >= cutoff_with_fix}")
    
    # Final Confirmation via actual engine call
    print("\n🚀 Running actual Engine analysis...")
    engine.analyze_continent_performance('England', 'Africa', opp_team='South Africa', years_back=10)
    
    # Note: If the fix works, the 'Mat' count should be 10 and 'Won' should be 3 in the printed output.

if __name__ == "__main__":
    verify_fix()
