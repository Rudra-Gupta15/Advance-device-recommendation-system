✨ Features
Dual-Category Intelligence: Specialized recommendation logic optimized for both Mobile and Laptop hardware.

Spec-Driven Filtering: Filter by budget, brand, storage, and specialized hardware (e.g., RTX Graphics for gaming).

Advanced Mode: Toggle between general user-friendly advice and spec-heavy technical filtering.

Side-by-Side Comparison: Integrated tool to compare two specific devices to assist in final decision-making.

Marketplace Integration: Dynamically generates search links for major platforms like Amazon and Flipkart.

Extensive Testing Suite: Includes various unit and flow tests (e.g., test_laptop_flow.py, test_api.py) to ensure recommendation accuracy.

🛠️ Tech Stack
Frontend: HTML5, CSS3 (Modern UI), JavaScript (ES6+), Inter Font.

Backend: Python 3.x, Flask, Flask-CORS.

Data Handling: Pandas for processing CSV-based datasets.

📁 Project Structure
Plaintext
device-recommendation/
├── versustech/
│   ├── backend/             # Flask API & Business Logic
│   │   ├── app.py           # Main Entry Point
│   │   ├── recommender.py   # Core Recommendation Engine
│   │   └── data/            # Local CSV Datasets
│   └── frontend/            # User Interface
│       ├── index.html       # Landing Page
│       ├── form.html        # Specification Input
│       ├── results.html     # Recommendation Display
│       ├── script.js        # API Integration & UI Logic
│       └── style.css        # Custom Styling
├── tests/                   # Extensive Test Suite
│   ├── test_laptop_flow.py  # End-to-end laptop logic test
│   ├── test_api.py          # API Endpoint validation
│   └── test_best_column.py  # Data processing validation
├── Recording_2026.mp4       # Project Demo Video
├── requirements.txt         # Project Dependencies
└── README.md
🚀 Getting Started
1. Clone the repository
Bash
git clone https://github.com/your-username/device-recommendation.git
cd device-recommendation
2. Set up the Environment
Bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
3. Install Dependencies
Bash
pip install -r requirements.txt
4. Run the Application
Start the backend: python versustech/backend/app.py

Open versustech/frontend/index.html in your browser.

🧪 Testing
The project includes several test scripts to verify the recommendation logic. You can run them individually to ensure the backend is behaving as expected:

Bash
python test_laptop_flow.py
python test_api.py
