import requests
import json

# Test for NaN values in JSON response
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
print("Testing for NaN values in JSON response")
print("=" * 80)

try:
    response = requests.post(url, json=payload)
    print(f"\nStatus Code: {response.status_code}")
    
    # Try to parse the response text as JSON
    response_text = response.text
    
    # Check if "NaN" appears in the raw text
    if "NaN" in response_text:
        print("\n❌ ERROR: Found NaN in response!")
        print(f"\nResponse snippet with NaN:\n{response_text[:500]}")
    else:
        print("\n✅ No NaN found in raw response text")
        
        # Try parsing as JSON
        try:
            data = response.json()
            print(f"✅ Valid JSON - Successfully parsed {len(data)} recommendations")
            
            if len(data) > 0:
                print("\n--- First Recommendation Sample ---")
                first = data[0]
                for key in list(first.keys())[:8]:  # Show first 8 keys
                    value = first[key]
                    value_type = type(value).__name__
                    print(f"{key}: {value} ({value_type})")
                
                print("\n✅✅ JSON PARSING SUCCESS - Frontend should work now!")
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON Parsing Error: {e}")
            print(f"Response text: {response_text[:500]}")
            
except Exception as e:
    print(f"\n❌ Connection Error: {e}")
