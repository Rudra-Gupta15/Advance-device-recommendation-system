import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'versustech', 'backend'))
from recommender import TechRecommender

def test_brand_preference():
    base_path = os.path.join(os.getcwd(), 'versustech', 'backend')
    recommender = TechRecommender(
        os.path.join(base_path, 'mobiles_large.csv'),
        os.path.join(base_path, 'laptops_large.csv'),
        None
    )

    # User scenario: OnePlus, 40k, Gaming, 8GB+, 256GB+
    print("Testing Brand Preference: OnePlus")
    results = recommender.get_recommendations(
        category='mobile',
        budget=40000,
        mode='advanced',
        preference='gaming',
        brand='OnePlus',
        min_ram=8,
        min_storage=256, 
        min_cpu=85,
        needs_rtx=False
    )
    
    oneplus_count = 0
    print(f"Top 5 Results:")
    for i, res in enumerate(results[:5]):
        print(f"{i+1}. {res['model']} (Price: {res['price']}) - Score: {res.get('final_score', 0):.2f}")
        if 'OnePlus' in res['model']:
            oneplus_count += 1

    if oneplus_count > 0:
        print(f"\nSUCCESS: Found {oneplus_count} OnePlus phones in top 5.")
    else:
        print("\nFAILURE: No OnePlus phones in top 5.")

if __name__ == "__main__":
    test_brand_preference()
