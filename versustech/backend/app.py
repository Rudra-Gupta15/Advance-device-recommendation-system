from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender import TechRecommender
import os

app = Flask(__name__)
CORS(app)

# Initialize recommender
base_path = os.path.dirname(os.path.abspath(__file__))
recommender = TechRecommender(
    os.path.join(base_path, 'mobiles.csv'),
    os.path.join(base_path, 'laptops.csv')
)

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    category = data.get('category')
    budget = float(data.get('budget'))
    mode = data.get('mode') # normal or advanced
    preferences = data.get('preferences', [])
    brand = data.get('brand')
    
    # New spec parameters
    min_ram = data.get('min_ram', 0)
    min_storage = data.get('min_storage', 0)
    min_cpu = data.get('min_cpu', 0)
    needs_rtx = data.get('needs_rtx', False)

    results = recommender.get_recommendations(
        category, budget, mode, preferences, brand,
        min_ram=min_ram, min_storage=min_storage, min_cpu=min_cpu, needs_rtx=needs_rtx
    )
    return jsonify(results)

@app.route('/api/compare', methods=['POST'])
def compare():
    data = request.json
    item1 = data.get('item1')
    item2 = data.get('item2')
    category = data.get('category')
    
    result = recommender.compare_products(item1, item2, category)
    return jsonify(result)

@app.route('/api/get_prices', methods=['GET'])
def get_prices():
    name = request.args.get('name')
    # Simulated prices/links as requested
    return jsonify({
        'amazon': f"https://www.amazon.in/s?k={name.replace(' ', '+')}",
        'flipkart': f"https://www.flipkart.com/search?q={name.replace(' ', '+')}",
        'official': f"https://www.google.com/search?q={name.replace(' ', '+')}+official+website"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
