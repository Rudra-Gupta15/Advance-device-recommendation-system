from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender import TechRecommender
import os

app = Flask(__name__)
CORS(app)

base_path = os.path.dirname(os.path.abspath(__file__))
recommender = TechRecommender(
    os.path.join(base_path, 'mobiles_large.csv'),
    os.path.join(base_path, 'laptops_large.csv'),
    None  # Disabled sales_data.csv - contains dummy/test data with gibberish names
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
    
    # Get Best Overall (ignoring brand)
    best_overall = recommender.get_best_overall(
        category, budget, min_ram=min_ram, min_storage=min_storage, min_cpu=min_cpu, mode=mode, needs_rtx=needs_rtx
    )
    
    return jsonify({
        'recommendations': results,
        'best_match': best_overall
    })

@app.route('/api/compare', methods=['POST'])
def compare():
    data = request.json
    item1 = data.get('item1')
    item2 = data.get('item2')
    category = data.get('category')
    
    result = recommender.compare_products(item1, item2, category)
    return jsonify(result)

@app.route('/api/catalog', methods=['GET'])
def catalog():
    """Get all devices grouped by brand for catalog view"""
    category = request.args.get('category', 'mobile')
    
    result = recommender.get_catalog(category)
    return jsonify(result)

@app.route('/api/get_prices', methods=['POST'])
def get_prices():
    # Simulated price links
    data = request.json
    product_name = data.get('name', '')
    
    return jsonify({
        'amazon': f'https://www.amazon.in/s?k={product_name}',
        'flipkart': f'https://www.flipkart.com/search?q={product_name}',
        'official': '#'
    })

@app.route('/api/options', methods=['POST'])
def get_options():
    data = request.json
    category = data.get('category', 'mobile')
    try:
        budget = float(data.get('budget', 0))
    except:
        budget = 0
        
    options = recommender.get_available_options(category, budget)
    return jsonify(options)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
