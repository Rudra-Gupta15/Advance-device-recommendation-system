# VersusTech | Smart Device Recommendation System 💻📱

VersusTech is a full-stack web application designed to help users navigate the crowded electronics market. By leveraging a Python-based recommendation engine, users can find the perfect mobile or laptop based on budget, technical specifications (RAM, CPU, GPU), and specific usage preferences.


## ✨ Features

-   **Dual-Category Support:** Specialized recommendation logic for both Mobiles and Laptops.
-   **Smart Filtering:** Filter by budget, brand, RAM, storage, and even specific needs like "RTX Graphics" for gamers.
-   **Advanced Mode:** Toggle between general recommendations and spec-heavy technical filtering.
-   **Product Comparison:** Side-by-side analysis of two devices to help make the final decision.
-   **Direct Marketplace Links:** Automatically generates search links for Amazon, Flipkart, and Official brand sites.

## 🛠️ Tech Stack

-   **Frontend:** HTML5, CSS3 (Modern UI with Inter font), JavaScript (ES6+).
-   **Backend:** Python 3.x, Flask, Flask-CORS.
-   **Data Management:** CSV-based dataset for lightweight and fast processing.

## 📁 Project Structure

```text
├── data/                   # Raw datasets for laptops and mobiles
├── versustech/
│   ├── backend/            # Flask API and Recommendation Logic
│   │   ├── app.py          # Main API Entry point
│   │   └── recommender.py  # Core recommendation algorithm
│   └── frontend/           # UI Components
│       ├── index.html      # Landing Page
│       ├── form.html       # Preference Input
│       └── script.js       # API Integration & UI Logic
└── requirements.txt        # Python dependencies
