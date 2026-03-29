# Crypto-Portfolio-Manager
CryptoMilestone is a Python-based crypto investment manager. It calculates optimal asset allocation, performs real-time risk analysis, predicts prices from historical trends, ensures portfolio diversification, uses parallel processing, SQLite storage, and CSV exports—no external ML needed.
Crypto Investment Manager

Python | Flask | Pandas | Scikit-Learn | SQLite

A full-stack, data-driven cryptocurrency analytics platform featuring automated ETL pipelines, portfolio optimization, and machine learning-based price forecasting.

Crypto Investment Manager is an end-to-end Python web application designed to simplify crypto investing. It programmatically fetches market data, performs statistical analysis, and provides actionable insights for investors. The system calculates optimal investment allocations, classifies asset risk, forecasts future prices using machine learning, and generates expected return timelines for major cryptocurrencies like Bitcoin, Ethereum, and Ripple.

The modular architecture separates heavy backend computations from the user interface, delivering insights through an intuitive, interactive web dashboard.

✨ System Features
# 💻 System & Security

Secure Authentication Pipeline: User registration and login with password hashing (Werkzeug) and session management via Flask.
SQLite Database: Stores user info, investments, and analytics data efficiently.

# 📊 Data Engineering & Analytics

Automated Data Ingestion: Fetches historical market data (up to 365 days) from the CoinGecko API.
Robust Data Processing: Cleans timestamps, handles missing values, and calculates daily returns, volatility, cumulative returns, and maximum drawdowns using Pandas.
Risk & ETA Modeling: Computes asset risk scores based on volatility and predicted returns, providing portfolio suggestions.
Smart Portfolio Mixer: Generates manual or auto-optimized portfolio allocations using risk-return analysis and Monte Carlo simulations.

# 🧠 Machine Learning Engine

Predictive Price Forecasting: Implements scikit-learn Linear Regression models to forecast future prices over user-defined horizons (e.g., 7–30 days).

# 🖥️ User Interface & Reporting

Interactive Data Visualization: Frontend uses Chart.js to render historical trends, portfolio allocation charts, and risk/return plots.
Automated Reports: Exports CSVs of processed data, investment allocations, and risk analyses for offline review.

# 🏗️ Architecture & Workflow

ETL → Inference → Presentation

Extract (data_collection.py): Pulls coin market data via CoinGecko API.
Transform (data_processing.py): Processes JSON data, calculates percent changes, rolling averages, and cumulative returns.
Inference (price_forecast.py / risk_checker.py):
Forecasts asset prices
Computes risk levels
Calculates expected portfolio returns and optimized allocations
Presentation (app.py / templates): Renders insights on the dashboard with tables, charts, and investment calculators.
# 🛠️ Technical Stack

Backend Framework: Python 3.8+, Flask, Flask-Login

Data Science & ML: Pandas, NumPy, Scikit-Learn

Database & ORM: SQLite, SQLAlchemy

External APIs: Requests (CoinGecko REST API)

Frontend: HTML + CSS + Jinja2 + JavaScript

# ⚙️ Quick Start Guide

Prerequisites: Python 3.8+ installed

Installation:
# Clone the repository
git clone https://github.com/vaishnavipawde633/crypto_investment_manager.git
cd crypto_investment_manager

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install Flask Flask-Login Flask-SQLAlchemy pandas numpy scikit-learn requests matplotlib
Execution:

# Crypto Investment Manager

## Repository Structure


```plaintext
crypto_investment_manager/
├── app.py
├── eda_analysis.py
├── milestone_logic.py
├── utils.py
├── database.db
├── templates/
│ ├── calculator.html
│ ├── dashboard.html
│ ├── forgot_password.html
│ ├── graphs.html
│ ├── login.html
│ ├── login_success.html
│ ├── predictor.html
│ ├── reset_password.html
│ ├── signup.html
│ └── summary.html
└── README.md
```
