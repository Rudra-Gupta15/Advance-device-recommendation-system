from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

# 1. Create Flask app
app = Flask(__name__)
CORS(app)  # allow frontend to talk to backend

# 2. Load datasets
mobiles = pd.read_csv("data/mobiles.csv")
laptops = pd.read_csv("data/laptops.csv")

# 3. Health check route
@app.route("/")
def home():
    return jsonify({
        "status": "Device Recommendation API is running"
    })

# 4. Recommendation endpoint
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()

    device_type = data.get("type")      # "mobile" or "laptop"
    budget = int(data.get("budget", 10**9))
    ram = float(data.get("ram", 0))

    # Select dataset
    if device_type == "mobile":
        df = mobiles
    elif device_type == "laptop":
        df = laptops
    else:
        return jsonify({"error": "Invalid device type"}), 400

    # Filter logic
    filtered = df[
        (df["price_inr"] <= budget) &
        (df["ram_gb"] >= ram)
    ].sort_values("rating", ascending=False)

    # Take top 5
    results = filtered.head(5)

    return jsonify(results.to_dict(orient="records"))

# 5. Run server
if __name__ == "__main__":
    app.run(debug=True)
