import requests
import json

def test_laptop():
    url = "http://127.0.0.1:5000/api/recommend"
    
    # Test Payload for Laptops
    payload = {
        "category": "laptop",
        "budget": 60000,
        "mode": "advanced",
        "preferences": ["gaming"], 
        "brand": None,
        "min_ram": 8,
        "min_storage": 512
    }

    print("Sending Laptop Request...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            
            recs = data.get('recommendations', [])
            best = data.get('best_match', [])
            
            print(f"\nReceived {len(recs)} Laptop recommendations.")
            
            if recs:
                r1 = recs[0]
                print(f"Top Laptop: {r1.get('model')}")
                print(f"  Price: {r1.get('price')}")
                print(f"  Specs: RAM={r1.get('ram')}GB, Storage={r1.get('storage')}GB, GPU={r1.get('gpu')}")
                # Verify Simulated Fields
                print(f"  Screen: {r1.get('screen_size')} (Should be ~13-17 inch)")
                print(f"  Weight: {r1.get('weight')} (Should be ~1.2-2.5 kg)")
                
                if not r1.get('weight'):
                    print("  ⚠️ WEIGHT MISSING!")
                else:
                    print("  ✅ Weight OK.")
                
                # Verify Logic Impact
                if 'gaming' in payload['preferences']:
                    # GPU should be high
                    print(f"  GPU Score implied: {r1.get('gpu')} (Should be dedicated for Gaming)")
            
            print(f"\nBest to Known (Count: {len(best)}):")
                
            print(f"\nBest to Known (Count: {len(best)}):")
            for b in best[:2]:
                print(f"  {b.get('model')} - {b.get('price')}")
                
        else:
            print(f"Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_laptop()
