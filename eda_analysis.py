# =========================================
# IMPORTS
# =========================================
import requests
import csv
from datetime import datetime
from collections import defaultdict

import pandas as pd
import matplotlib.pyplot as plt


# =========================================
# DATA FETCH + CSV CREATION
# =========================================

COINS = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "ripple": "Ripple",
    "litecoin": "Litecoin"
}

DAYS = 90
CURRENCY = "inr"

all_rows = []
best_coin_table = []
daily_percent_change = defaultdict(dict)

for coin_id, coin_name in COINS.items():
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": CURRENCY, "days": DAYS}

    data = requests.get(url, params=params).json()
    prices = data["prices"]

    daily_prices = defaultdict(list)
    for t, p in prices:
        d = datetime.fromtimestamp(t / 1000).date()
        daily_prices[d].append(p)

    prev_close = None
    for d in sorted(daily_prices):
        day_prices = daily_prices[d]

        open_p = day_prices[0]
        close_p = day_prices[-1]
        high_p = max(day_prices)
        low_p = min(day_prices)

        if prev_close is not None:
            pct = ((close_p - prev_close) / prev_close) * 100

        else:
            pct = 0.0

        all_rows.append([
            str(d),
            coin_name,
            round(open_p, 2),
            round(close_p, 2),
            round(high_p, 2),
            round(low_p, 2),
            round(pct, 2)
        ])

        if prev_close is not None:
            daily_percent_change[d][coin_name] = round(pct, 2)

        prev_close = close_p


# =========================================
# BEST COIN PER DAY TABLE
# =========================================
for d in sorted(daily_percent_change):
    best_coin = max(daily_percent_change[d], key=daily_percent_change[d].get)
    best_pct = daily_percent_change[d][best_coin]

    best_coin_table.append([
        str(d),
        best_coin,
        best_pct
    ])


# =========================================
# WRITE CSV (TWO TABLES IN ONE FILE)
# =========================================
with open("crypto_all_data_with_best_coin_table.csv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t")

    writer.writerow([
        "Date",
        "Coin",
        "OpenPrice",
        "ClosePrice",
        "HighPrice",
        "LowPrice",
        "PercentChange"
    ])
    writer.writerows(all_rows)

    writer.writerow([])
    writer.writerow([])

    writer.writerow([
        "Date",
        "BestCoin",
        "PercentChange"
    ])
    writer.writerows(best_coin_table)

print("CSV saved with separate Best Coin table at the bottom")


# =========================================
# PART 2: EDA + VISUALIZATION
# =========================================

file_path = "crypto_all_data_with_best_coin_table.csv"
df = pd.read_csv(file_path, sep="\t")

df = df[df["Coin"].notna()]
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

numeric_cols = ["OpenPrice", "ClosePrice", "HighPrice", "LowPrice", "PercentChange"]
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

print("\nDATA LOADED SUCCESSFULLY")
print(df.head())


# =========================================
# BASIC EDA
# =========================================
print("\nDATA SHAPE:", df.shape)
print("\nCOLUMNS:\n", df.columns)
print("\nMISSING VALUES:\n", df.isnull().sum())
print("\nDATA TYPES:\n", df.dtypes)

print("\nDESCRIPTIVE STATISTICS:")
print(df.describe())


# =========================================
# PERFORMANCE & RISK
# =========================================
returns_df = df.pivot_table(
    index="Date",
    columns="Coin",
    values="PercentChange"
)

avg_return = returns_df.mean()
volatility = returns_df.std()

print("\nAVERAGE DAILY RETURN (%):")
print(avg_return)

print("\nVOLATILITY (STD DEV):")
print(volatility)

# =========================================
# BEST COIN FREQUENCY
# =========================================
best_daily = df.loc[df.groupby("Date")["PercentChange"].idxmax()]
best_frequency = best_daily["Coin"].value_counts()

print("\nBEST COIN FREQUENCY:")
print(best_frequency)


# =========================================
# PRICE TRENDS (SEPARATE)
# =========================================
plot_df = df.dropna(subset=["ClosePrice"])

for coin in plot_df["Coin"].unique():
    data = plot_df[plot_df["Coin"] == coin]
    plt.figure()
    plt.plot(data["Date"], data["ClosePrice"])
    plt.title(f"{coin} Price Trend (INR)")
    plt.xlabel("Date")
    plt.ylabel("Close Price (INR)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# =========================================
# 7-DAY MOVING AVERAGE
# =========================================
plot_df = df.dropna(subset=["ClosePrice"]).copy()
plot_df["MA_7"] = plot_df.groupby("Coin")["ClosePrice"].transform(
    lambda x: x.rolling(window=7).mean()
)

plt.figure()
for coin in plot_df["Coin"].unique():
    data = plot_df[plot_df["Coin"] == coin]
    plt.plot(data["Date"], data["MA_7"], label=coin)

plt.title("7-Day Moving Average of Crypto Prices")
plt.xlabel("Date")
plt.ylabel("Price (INR)")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# =========================================
# MISSING DATA REPORT
# =========================================
print("\nMISSING DATA REPORT (by Coin):")
missing_report = (
    df[["Coin", "ClosePrice", "HighPrice", "LowPrice", "PercentChange"]]
    .isnull()
    .groupby(df["Coin"])
    .sum()
)
print(missing_report)


# =========================================
# RETURN DISTRIBUTION
# =========================================
plt.figure()
df.boxplot(column="PercentChange", by="Coin")
plt.title("Daily Return Distribution by Coin")
plt.suptitle("")
plt.xlabel("Coin")
plt.ylabel("Daily % Change")
plt.tight_layout()
plt.show()


# =========================================
# CORRELATION ANALYSIS
# =========================================
pivot = df.pivot_table(
    index="Date",
    columns="Coin",
    values="ClosePrice",
    aggfunc="mean"
)

print("\nPRICE CORRELATION MATRIX:")
print(pivot.corr())


# =========================================
# CUMULATIVE RETURNS
# =========================================
df["CumulativeReturn"] = (
    (1 + df["PercentChange"] / 100)
    .groupby(df["Coin"])
    .cumprod()
)

plt.figure()
for coin in df["Coin"].unique():
    data = df[df["Coin"] == coin]
    plt.plot(data["Date"], data["CumulativeReturn"], label=coin)

plt.title("Cumulative Returns Over Time")
plt.xlabel("Date")
plt.ylabel("Growth of 1 Unit Investment")
plt.legend()
plt.tight_layout()
plt.show()


# =========================================
# MAXIMUM DRAWDOWN
# =========================================
print("\nMAXIMUM DRAWDOWN (%):")
drawdowns = {}

for coin in df["Coin"].unique():
    data = df[df["Coin"] == coin].copy()
    rolling_max = data["ClosePrice"].cummax()
    drawdown = (data["ClosePrice"] - rolling_max) / rolling_max
    drawdowns[coin] = drawdown.min() * 100
    print(f"{coin}: {drawdowns[coin]:.2f}%")


# =========================================
# RISK-ADJUSTED RETURN
# =========================================
risk_adjusted = avg_return / volatility
best_coin_overall = best_frequency.idxmax()

print("\nRISK-ADJUSTED RETURN:")
print(risk_adjusted)

plt.figure()
plt.scatter(volatility, avg_return)

for coin in avg_return.index:
    plt.text(volatility[coin], avg_return[coin], coin)

plt.scatter(
    volatility[best_coin_overall],
    avg_return[best_coin_overall],
    s=200,
    marker="*"
)
plt.text( volatility[best_coin_overall], 
         avg_return[best_coin_overall] , 
         f" BEST: {best_coin_overall}", 
         fontsize=11, 
         fontweight="bold", 
         ha="center"
)
plt.title("Risk vs Return Analysis of Cryptocurrencies")
plt.xlabel("Risk (Volatility)")
plt.ylabel("Average Daily Return (%)")
plt.grid(True)
plt.tight_layout()
plt.show()


# =========================================
# FINAL CONCLUSION
# =========================================
print("\nFINAL EDA CONCLUSION:")
print(f"Most frequently best-performing coin: {best_coin_overall}")
print("Higher return = better performance")
print("Higher volatility = higher risk")
print("Risk-adjusted return balances both")





# =========================================
# MILESTONE 2 – SMART PORTFOLIO SYSTEM
# =========================================

print("\nMILESTONE 2: INVESTMENT MIX CALCULATOR")
print("Choose Mode:")
print("1 → Manual Analysis (Enter your own weights)")
print("2 → Efficient Portfolio (Auto-Optimized)")

choice = input("Enter 1 or 2: ")

# =====================================================
# OPTION 1 – MANUAL USER INPUT
# =====================================================
if choice == "1":

    print("\nEnter portfolio weights (must sum to 1.0)\n")

    portfolio_weights = {}

    for coin in avg_return.index:
        while True:
            try:
                weight = float(input(f"Enter weight for {coin}: "))
                if weight < 0:
                    print("Weight cannot be negative.")
                    continue
                portfolio_weights[coin] = weight
                break
            except ValueError:
                print("Invalid input.")

    total_weight = sum(portfolio_weights.values())

    if round(total_weight, 2) != 1.0:
        print(f"\nERROR: Total weight = {total_weight:.2f}")
        print("Weights must sum to 1.0")
        exit()

# =====================================================
# OPTION 2 – EFFICIENT (AUTO)
# =====================================================
elif choice == "2":

    print("\nChoose Optimization Goal:")
    print("1 → Maximize Return")
    print("2 → Minimize Risk")
    print("3 → Balanced Strategy")

    opt_choice = input("Enter 1, 2 or 3: ")

    portfolio_weights = {}

    # ------------------------------
    # Max Return
    # ------------------------------
    if opt_choice == "1":

        best_coin = avg_return.idxmax()

        for coin in avg_return.index:
            portfolio_weights[coin] = 1.0 if coin == best_coin else 0.0

        print(f"\nMax Return Strategy: 100% allocated to {best_coin}")

    # ------------------------------
    # Min Risk
    # ------------------------------
    elif opt_choice == "2":

        safest_coin = volatility.idxmin()

        for coin in avg_return.index:
            portfolio_weights[coin] = 1.0 if coin == safest_coin else 0.0

        print(f"\nMinimum Risk Strategy: 100% allocated to {safest_coin}")

    # ------------------------------
    # Balanced Strategy
    # ------------------------------
    elif opt_choice == "3":

        print("\nBalanced Strategy Mode:")
        print("1 → Invest 100% in Most Efficient Coin")
        print("2 → Create Diversified Optimized Portfolio")

        sub_choice = input("Enter 1 or 2: ")

        returns_df = df.pivot_table(
            index="Date",
            columns="Coin",
            values="PercentChange"
        )

        mean_returns = returns_df.mean()
        cov_matrix = returns_df.cov()

        # 100% Most Efficient Coin
        if sub_choice == "1":

            safe_volatility = volatility.replace(0, 1e-8)
            risk_adjusted = avg_return / safe_volatility

            best_coin = risk_adjusted.idxmax()

            for coin in avg_return.index:
                portfolio_weights[coin] = 1.0 if coin == best_coin else 0.0

            print(f"\nSelected Most Efficient Coin: {best_coin}")

        # Diversified Optimized Portfolio
        elif sub_choice == "2":

            import numpy as np

            max_coins = len(mean_returns)

            while True:
                try:
                    n_coins = int(input(f"How many coins to include? (1 to {max_coins}): "))
                    if 1 <= n_coins <= max_coins:
                        break
                    else:
                        print("Invalid number.")
                except ValueError:
                    print("Enter a valid integer.")

            num_portfolios = 5000
            best_sharpe = -999
            best_weights = None

            for _ in range(num_portfolios):

                weights = np.random.random(len(mean_returns))
                weights /= np.sum(weights)

                # Keep only top N weights
                top_indices = np.argsort(weights)[-n_coins:]
                filtered_weights = np.zeros_like(weights)
                filtered_weights[top_indices] = weights[top_indices]
                filtered_weights /= np.sum(filtered_weights)

                portfolio_return_temp = np.sum(filtered_weights * mean_returns)

                portfolio_risk_temp = np.sqrt(
                    np.dot(filtered_weights.T, np.dot(cov_matrix, filtered_weights))
                )

                sharpe_ratio = (
                    portfolio_return_temp / portfolio_risk_temp
                    if portfolio_risk_temp != 0 else 0
                )

                if sharpe_ratio > best_sharpe:
                    best_sharpe = sharpe_ratio
                    best_weights = filtered_weights

            for coin, weight in zip(mean_returns.index, best_weights):
                portfolio_weights[coin] = weight

            print("\nOptimized Diversified Portfolio:")
            for coin, weight in portfolio_weights.items():
                if weight > 0:
                    print(f"{coin}: {weight*100:.2f}%")

        else:
            print("Invalid choice.")
            exit()

    else:
        print("Invalid choice.")
        exit()

else:
    print("Invalid choice.")
    exit()


# =====================================================
# CALCULATE PORTFOLIO PERFORMANCE
# =====================================================

# Portfolio Return
returns_df = df.pivot_table(
    index="Date",
    columns="Coin",
    values="PercentChange"
)

mean_returns = returns_df.mean()
cov_matrix = returns_df.cov()

weights_array = [portfolio_weights[coin] for coin in mean_returns.index]

import numpy as np
weights_array = np.array(weights_array)

portfolio_return = np.sum(weights_array * mean_returns)

portfolio_risk = np.sqrt(
    np.dot(weights_array.T, np.dot(cov_matrix, weights_array))
)


# Portfolio Variance
portfolio_variance = 0

for i in portfolio_weights:
    for j in portfolio_weights:
        portfolio_variance += (
            portfolio_weights[i]
            * portfolio_weights[j]
            * cov_matrix.loc[i, j]
        )

portfolio_risk = portfolio_variance ** 0.5

print(f"\nPortfolio Expected Return: {portfolio_return:.4f} %")
print(f"Portfolio Risk (Volatility): {portfolio_risk:.4f}")
# =====================================================
# INVESTMENT ALLOCATION CALCULATOR
# =====================================================

while True:
    try:
        total_investment = float(input("\nEnter total amount you want to invest (₹): "))
        if total_investment <= 0:
            print("Investment must be positive.")
            continue
        break
    except ValueError:
        print("Enter a valid number.")

print("\nINVESTMENT ALLOCATION RECOMMENDATION")
print("======================================")

expected_profit = 0

for coin, weight in portfolio_weights.items():
    amount = total_investment * weight
    coin_return = avg_return[coin]
    profit = amount * (coin_return / 100)

    expected_profit += profit

    print(f"{coin}")
    print(f"  Allocation: ₹{amount:,.2f}")
    print(f"  Weight: {weight*100:.1f}%")
    print(f"  Expected Daily Return: {coin_return:.2f}%")
    print(f"  Expected Daily Profit: ₹{profit:,.2f}")
    print("--------------------------------------")

print(f"Total Investment: ₹{total_investment:,.2f}")
print(f"Estimated Portfolio Daily Profit: ₹{expected_profit:,.2f}")
print("======================================")


# =====================================================
# PROFESSIONAL RISK vs RETURN GRAPH
# =====================================================

plt.figure(figsize=(12, 8))

# Plot individual coins
plt.scatter(volatility, avg_return, s=150)

for coin in avg_return.index:
    plt.annotate(
        coin,
        (volatility[coin], avg_return[coin]),
        textcoords="offset points",
        xytext=(6, 6),
        fontsize=9
    )

# Highlight Best Return Coin
best_coin = avg_return.idxmax()
plt.scatter(
    volatility[best_coin],
    avg_return[best_coin],
    s=300,
    marker="*"
)

plt.annotate(
    "BEST RETURN",
    (volatility[best_coin], avg_return[best_coin]),
    textcoords="offset points",
    xytext=(10, -10),
    fontweight="bold"
)

# Plot Portfolio
plt.scatter(
    portfolio_risk,
    portfolio_return,
    s=300,
    marker="D"
)
   

# Titles and labels
plt.title("Risk vs Return Analysis", fontsize=14)
plt.xlabel("Risk (Volatility)", fontsize=12)
plt.ylabel("Average Daily Return (%)", fontsize=12)
plt.grid(True)

plt.subplots_adjust(top=0.90, bottom=0.12)
plt.show()

