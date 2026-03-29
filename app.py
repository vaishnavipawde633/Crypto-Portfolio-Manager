# ===================== app.py =====================
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from milestone_logic import (
    fetch_daily_crypto_data,
    fetch_daily_best_coin,
    calculate_investment_mix,
    calculate_risk_and_prediction,
    get_risk_results,
    apply_diversification_and_stress,
    run_stress_tests,
    predict_future_price
)
from utils import check_crypto_alerts

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Change for production

DATABASE = "database.db"

# ===================== DATABASE UTILS =====================
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            coin TEXT NOT NULL,
            amount REAL NOT NULL,
            allocation REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ===================== ROUTES =====================

# -------- HOME --------
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

# -------- LOGIN --------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

# -------- SIGNUP --------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        try:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, password)
            )
            conn.commit()
            conn.close()
            flash("Account created! Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username or email already exists", "danger")
    return render_template('signup.html')

# -------- DASHBOARD --------
## ======== UPDATED DASHBOARD ROUTE ========
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # 1. Daily Best Performers
    best_coin_data = fetch_daily_best_coin()

    # 2. Today's returns
    today_returns = {item['coin']: item['change'] for item in best_coin_data}

    # 3. Recommended Investment Mix
    investment_mix = calculate_investment_mix(today_returns)

    # 4. Risk Analysis
    risk_results = get_risk_results(today_returns)

    # === USER'S ACTUAL INVESTMENTS ===
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT coin, SUM(amount) as total_amount
        FROM investments 
        WHERE user_id = ? 
        GROUP BY coin
    ''', (session['user_id'],)).fetchall()
    conn.close()

    user_investment_table = []
    total_invested = sum(float(row['total_amount']) for row in rows if row['total_amount'])

    for row in rows:
        total_amount = round(float(row['total_amount']), 2)
        allocation = round((total_amount / total_invested * 100), 2) if total_invested > 0 else 0.0

        user_investment_table.append({
            "coin": row['coin'],
            "amount": total_amount,
            "allocation": allocation
        })

    # Prepare tables
    investment_table = []
    for coin, alloc in investment_mix.items():
        risk_score = risk_results.get(coin, {}).get("Risk", 0)
        risk_level = "Low Risk" if risk_score <= 3 else "Medium Risk" if risk_score <= 6 else "High Risk"
        investment_table.append({
            "coin": coin,
            "allocation": round(alloc, 2),
            "risk": risk_level
        })

    risk_table = []
    for coin, data in risk_results.items():
        suggestion = "Hold"
        if data.get("Risk", 0) > 5:
            suggestion = "Reduce Exposure"
        elif data.get("Predicted Return", 0) > 1:
            suggestion = "Increase Allocation"
        risk_table.append({
            "coin": coin,
            "risk": round(data.get("Risk", 0), 1),
            "predicted": round(data.get("Predicted Return", 0), 2),
            "suggestion": suggestion
        })

    # === Send Crypto Alerts ===
    conn = get_db_connection()
    user = conn.execute('SELECT email FROM users WHERE id = ?', 
                       (session['user_id'],)).fetchone()
    conn.close()

    if user and user['email']:
        check_crypto_alerts(today_returns, user['email'])

    # Render (Stress Test already removed)
    return render_template(
        "dashboard.html",
        best_coin_data=best_coin_data,
        investment_table=investment_table,
        risk_table=risk_table,
        user_investments=user_investment_table
    )

# -------- LOGOUT --------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))

# -------- CALCULATOR (OPTIONAL) --------
# -------- CALCULATOR --------
# -------- CALCULATOR --------
@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    result = None

    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            coin = request.form['coin']
            allocation = float(request.form['allocation'])

            # Calculate invested amount
            invested_amount = round(amount * allocation / 100, 2)
            result = invested_amount

            # Save investment to database
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO investments (user_id, coin, amount, allocation)
                VALUES (?, ?, ?, ?)
            ''', (session['user_id'], coin, invested_amount, allocation))
            conn.commit()
            conn.close()

            flash(f"₹ {invested_amount:,} invested in {coin} successfully!", "success")
            
            # IMPORTANT: Redirect to dashboard so user can see the investment immediately
            return redirect(url_for('dashboard'))

        except Exception as e:
            result = "Invalid input!"
            flash("Error saving investment. Please check your inputs.", "danger")

    # For GET request (first time opening calculator)
    return render_template('calculator.html', result=result)




# -------- PREDICTOR --------
# -------- PREDICTOR --------
@app.route('/predictor', methods=['GET', 'POST'])
def predictor():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    prediction = None
    selected_coin = "Bitcoin"
    days_ahead = 7

    if request.method == 'POST':
        selected_coin = request.form.get('coin', 'Bitcoin')
        try:
            days_ahead = int(request.form.get('days_ahead', 7))
            days_ahead = max(1, min(30, days_ahead))
        except:
            days_ahead = 7

        # Now this will work
        prediction = predict_future_price(coin_name=selected_coin, days_ahead=days_ahead)

    return render_template('predictor.html', 
                           prediction=prediction,
                           selected_coin=selected_coin,
                           days_ahead=days_ahead)


# -------- SUMMARY --------
@app.route('/summary')
def summary():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    best_coin_data = fetch_daily_best_coin()
    
    today_returns = {item['coin']: item['change'] for item in best_coin_data} if best_coin_data else {}

    investment_mix = calculate_investment_mix(today_returns)
    risk_results = get_risk_results(today_returns)
    stress_results = run_stress_tests(investment_mix, risk_results)   # optional

    # Latest prediction for Bitcoin (you can change to dynamic later)
    latest_prediction = predict_future_price(coin_name="Bitcoin", days_ahead=7)

    # Convert investment_mix dict → list (to match dashboard)
    investment_table = []
    for coin, alloc in investment_mix.items():
        investment_table.append({"coin": coin, "allocation": round(alloc, 2)})

    # Convert risk_results to list (to match dashboard)
    risk_table = []
    for coin, data in risk_results.items():
        suggestion = "Hold"
        if data.get("Risk", 0) > 5:
            suggestion = "Reduce Exposure"
        elif data.get("Predicted Return", 0) > 1:
            suggestion = "Increase Allocation"
        risk_table.append({
            "coin": coin,
            "risk": round(data.get("Risk", 0), 1),
            "predicted": round(data.get("Predicted Return", 0), 2),
            "suggestion": suggestion
        })

    return render_template('summary.html',
                           investment_table=investment_table,
                           risk_table=risk_table,
                           best_coin_data=best_coin_data,
                           prediction=latest_prediction)


# ===================== MAIN =====================
if __name__ == '__main__':
    init_db()
    app.run(debug=True)