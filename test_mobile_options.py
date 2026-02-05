import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'versustech', 'backend'))
from recommender import TechRecommender

def test_mobile_options():
    base_path = os.path.join(os.getcwd(), 'versustech', 'backend')
    recommender = TechRecommender(
        os.path.join(base_path, 'mobiles_large.csv'),
        os.path.join(base_path, 'laptops_large.csv'),
        None
    )

    print("Testing Options for Mobile (Any Budget)")
    opts = recommender.get_available_options('mobile', 50000)
    
    expected_ram = [4, 6, 8, 12, 16]
    expected_storage = [32, 64, 128, 256]
    
    print(f"RAM Options: {opts['ram']}")
    print(f"Storage Options: {opts['storage']}")
    
    if opts['ram'] == expected_ram and opts['storage'] == expected_storage:
        print("\nSUCCESS: Mobile options are strictly enforced.")
    else:
        print("\nFAILURE: Options do not match expected standard sets.")

    print("\nTesting Options for Laptop (Should be dynamic/different)")
    opts_lap = recommender.get_available_options('laptop', 50000)
    print(f"Laptop RAM: {opts_lap['ram']}")
    
    if opts_lap['ram'] != expected_ram:
        print("SUCCESS: Laptop options remain dynamic.")

if __name__ == "__main__":
    test_mobile_options()
