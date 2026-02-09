import requests
import json

def test_submission():
    url = "http://127.0.0.1:5000/api/recommend"
    
    # Simulate payload from Mobile form where 'mode' and 'min_cpu' might be defaults or hidden
    # "mode" and "min_cpu_score" are usually sent by correct frontend, but let's see if defaults work
    # Actually frontend sends valid defaults even if hidden
    
    payload = {
        "category": "mobile",
        "budget": 30000,
        "mode": "normal", # Default value from hidden select
        "preferences": [],
        "brand": "OnePlus",
        "min_ram": 8,     # Strict option
        "min_storage": 128, # Strict option
        "min_cpu": 0,    # Default value from hidden select
        "needs_rtx": False
    }

    print("Sending Mobile Payload:", json.dumps(payload, indent=2))
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"\nSUCCESS: Received {len(data)} recommendations.")
            if len(data) > 0:
                print("Top pick:", data[0]['model'])
        else:
            print(f"\nFAILED: Status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_submission()
