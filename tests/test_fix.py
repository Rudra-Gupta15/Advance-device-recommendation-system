import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'versustech', 'backend'))
from recommender import TechRecommender

def test_iqoo_recommendation():
    base_path = os.path.join(os.getcwd(), 'versustech', 'backend')
    recommender = TechRecommender(
        os.path.join(base_path, 'mobiles_large.csv'),
        os.path.join(base_path, 'laptops_large.csv'),
        None
    )

    # User scenario: IQOO, 60k, 8GB+, 256GB+
    # Before fix: 0 results (due to strict storage filter)
    # After fix: Should return IQOO phones
    results = recommender.get_recommendations(
        category='mobile',
        budget=60000,
        mode='advanced',
        preference='gaming',
        brand='IQOO',
        min_ram=8,
        min_storage=256, # This caused the issue
        min_cpu=85,
        needs_rtx=False
    )

    print(f"Found {len(results)} recommendations.")
    for res in results:
        print(f"- {res['model']} (Price: {res['price']}, RAM: {res['ram']}, Storage: {res['storage']})")
    
    if len(results) > 0:
        print("\nSUCCESS: Recommendations found despite missing storage data.")
    else:
        print("\nFAILURE: No recommendations found.")

if __name__ == "__main__":
    test_iqoo_recommendation()
