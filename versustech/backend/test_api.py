import requests
import json

# Test the recommendation endpoint with verbose output
url = "http://127.0.0.1:5000/api/recommend"
payload = {
    "category": "mobile",
    "budget": 30000,
    "mode": "normal",
    "preferences": [],
    "brand": "",
    "min_ram": 0,
    "min_storage": 0,
    "min_cpu": 0,
    "needs_rtx": False
}

print("=" * 80)
print("Testing Mobile Recommendations API")
print("=" * 80)

try:
    response = requests.post(url, json=payload)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nNumber of recommendations: {len(data)}")
        
        if len(data) > 0:
            print("\n--- First Recommendation ---")
            first_item = data[0]
            for key, value in first_item.items():
                print(f"{key}: {value}")
            
            print("\n✅ Backend is working correctly!")
        else:
            print("\n⚠️ No recommendations returned")
    else:
        print(f"\n❌ Error: {response.text}")
        
except Exception as e:
    print(f"\n❌ Connection Error: {e}")

print("\n" + "=" * 80)
print("Testing Laptop Recommendations API")
print("=" * 80)

payload["category"] = "laptop"
payload["budget"] = 60000

try:
    response = requests.post(url, json=payload)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nNumber of recommendations: {len(data)}")
        
        if len(data) > 0:
            print("\n--- First Recommendation ---")
            first_item = data[0]
            for key, value in first_item.items():
                print(f"{key}: {value}")
            
            print("\n✅ Backend is working correctly!")
        else:
            print("\n⚠️ No recommendations returned")
    else:
        print(f"\n❌ Error: {response.text}")
        
except Exception as e:
    print(f"\n❌ Connection Error: {e}")
