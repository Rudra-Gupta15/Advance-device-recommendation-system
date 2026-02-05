import requests
import json
import time

def test_redesign():
    url = "http://127.0.0.1:5000/api/recommend"
    
    payload = {
        "category": "mobile",
        "budget": 40000,
        "mode": "advanced",
        "preferences": ["gaming"],
        "brand": "OnePlus",
        "min_ram": 8,
        "min_storage": 128
    }

    print("Sending Request...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            
            recs = data.get('recommendations', [])
            best_list = data.get('best_match')
            
            print(f"\nReceived {len(recs)} main recommendations.")
            
            # Verify Best Match List
            if isinstance(best_list, list):
                print(f"✅ 'best_match' is a LIST (Length: {len(best_list)})")
                if len(best_list) > 1:
                    print("✅ 'best_match' contains multiple items (Expanded Best to Known)")
                else:
                    print("⚠️ 'best_match' has 1 or 0 items. (Check limit or data availability)")
                
                print("\nTop 3 Best Matches:")
                for i, item in enumerate(best_list[:3]):
                    print(f"  {i+1}. {item['model']} (Price: {item['price']}, Storage: {item.get('storage')}GB, Screen: {item.get('screen_size')}, Battery: {item.get('battery')}mAh)")
                    if item.get('storage', 0) == 0:
                        print("     ⚠️ STORAGE IS STILL 0!")
                    else:
                        print("     ✅ Storage found.")
            else:
                print("❌ 'best_match' is NOT a list! (Backend update incorrect?)")
                print(f"Type: {type(best_list)}")
                
        else:
            print(f"Failed: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_redesign()
