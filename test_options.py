import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'versustech', 'backend'))
from recommender import TechRecommender

def test_dynamic_options():
    base_path = os.path.join(os.getcwd(), 'versustech', 'backend')
    recommender = TechRecommender(
        os.path.join(base_path, 'mobiles_large.csv'),
        os.path.join(base_path, 'laptops_large.csv'),
        None
    )

    # Test Case 1: Low Budget (Should only show low RAM/Storage)
    print("Testing Options for Budget: 10,000")
    opts_low = recommender.get_available_options('mobile', 10000)
    print(f"RAM Options: {opts_low['ram']}")
    print(f"Storage Options: {opts_low['storage']}")
    
    # Test Case 2: High Budget (Should show high RAM/Storage)
    print("\nTesting Options for Budget: 60,000")
    opts_high = recommender.get_available_options('mobile', 60000)
    print(f"RAM Options: {opts_high['ram']}")
    print(f"Storage Options: {opts_high['storage']}")

    # Validation
    if max(opts_low['ram']) < max(opts_high['ram']):
        print("\nSUCCESS: Low budget offers fewer/lower RAM options than high budget.")
    else:
        print("\nWARNING: RAM options did not change significantly (check dataset).")

if __name__ == "__main__":
    test_dynamic_options()
