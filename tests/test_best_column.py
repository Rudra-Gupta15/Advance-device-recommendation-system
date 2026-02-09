import requests
import json
import time

def test_best_column():
    url = "http://127.0.0.1:5000/api/recommend"
    
    # Payload: Mobile, 35k budget, Brand Preference "OnePlus"
    # We expect Recommendations to be OnePlus
    # We expect Best Match to be maybe Realme or IQOO (better specs for price)
    payload = {
        "category": "mobile",
        "budget": 35000,
        "mode": "advanced",
        "preferences": ["gaming"],
        "brand": "OnePlus",
        "min_ram": 8,
        "min_storage": 128
    }

    print("Sending Request with Brand='OnePlus'...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            
            recs = data.get('recommendations', [])
            best = data.get('best_match')
            
            print(f"\nReceived {len(recs)} recommendations.")
            if recs:
                print(f"Top Recommendation: {recs[0]['model']} (Score: {recs[0]['final_score']:.2f})")
            
            if best:
                print(f"\nBest to Known (Overall): {best['model']} (Score: {best['final_score']:.2f})")
                
                # Verification
                if "OnePlus" in recs[0]['model']:
                    print("✅ Top Recommendation respects Brand Preference (OnePlus)")
                else:
                    print("⚠️ Top Recommendation is NOT OnePlus (Check brand logic)")
                    
                if best['model'] != recs[0]['model']:
                    print("✅ 'Best to Known' is different from Top Rec (Found a better spec phone!)")
                else:
                    print("ℹ️ 'Best to Known' is the same as Top Rec (OnePlus might be the best anyway)")
            else:
                print("❌ No 'Best to Known' returned!")
                
        else:
            print(f"Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_best_column()
