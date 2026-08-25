"""
RetailPulse - Synthetic Data Generator
Generates realistic retail transactions, customer, and inventory data
for demand forecasting, churn prediction, and segmentation.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

np.random.seed(42)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT_DIR, exist_ok=True)

N_CUSTOMERS = 3000
N_PRODUCTS = 60
CATEGORIES = ["Electronics", "Grocery", "Apparel", "Home & Kitchen", "Beauty", "Sports"]
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2026, 6, 30)
N_DAYS = (END_DATE - START_DATE).days


def generate_products():
    products = []
    for pid in range(1, N_PRODUCTS + 1):
        cat = np.random.choice(CATEGORIES)
        base_price = {
            "Electronics": np.random.uniform(50, 800),
            "Grocery": np.random.uniform(2, 40),
            "Apparel": np.random.uniform(10, 120),
            "Home & Kitchen": np.random.uniform(15, 250),
            "Beauty": np.random.uniform(5, 90),
            "Sports": np.random.uniform(10, 300),
        }[cat]
        products.append({
            "product_id": f"P{pid:04d}",
            "category": cat,
            "unit_price": round(base_price, 2),
            "base_daily_demand": np.random.uniform(1, 25),
            "seasonality_amp": np.random.uniform(0.1, 0.6),
            "trend": np.random.uniform(-0.0003, 0.0008),
            "current_stock": np.random.randint(50, 500),
            "lead_time_days": np.random.choice([3, 5, 7, 10, 14]),
        })
    return pd.DataFrame(products)


def generate_customers():
    customers = []
    for cid in range(1, N_CUSTOMERS + 1):
        signup = START_DATE + timedelta(days=int(np.random.uniform(0, N_DAYS * 0.7)))
        segment_seed = np.random.choice(
            ["champion", "loyal", "at_risk", "new", "occasional", "lost"],
            p=[0.08, 0.17, 0.15, 0.15, 0.30, 0.15]
        )
        customers.append({
            "customer_id": f"C{cid:05d}",
            "signup_date": signup,
            "age": np.random.randint(18, 70),
            "city_tier": np.random.choice(["Tier1", "Tier2", "Tier3"], p=[0.4, 0.35, 0.25]),
            "acquisition_channel": np.random.choice(["Organic", "Paid Ads", "Referral", "Social"]),
            "_behavior_seed": segment_seed,
        })
    return pd.DataFrame(customers)


def generate_transactions(customers_df, products_df):
    behavior_params = {
        "champion":  dict(freq=3.5, recency_bias=0.95, aov_mult=1.6, churn_prob=0.02),
        "loyal":     dict(freq=2.0, recency_bias=0.85, aov_mult=1.2, churn_prob=0.05),
        "at_risk":   dict(freq=1.2, recency_bias=0.35, aov_mult=1.0, churn_prob=0.55),
        "new":       dict(freq=1.5, recency_bias=0.75, aov_mult=0.9, churn_prob=0.20),
        "occasional":dict(freq=0.8, recency_bias=0.55, aov_mult=0.85, churn_prob=0.30),
        "lost":      dict(freq=0.3, recency_bias=0.05, aov_mult=0.8, churn_prob=0.92),
    }

    rows = []
    order_id = 1
    products = products_df.to_dict("records")

    for _, cust in customers_df.iterrows():
        params = behavior_params[cust["_behavior_seed"]]
        days_active = (END_DATE - cust["signup_date"]).days
        if days_active <= 0:
            continue
        # Expected number of orders scaled by recency_bias (whether they're still active)
        n_orders = np.random.poisson(max(params["freq"] * (days_active / 90) * params["recency_bias"], 0.1))
        n_orders = min(n_orders, 120)

        last_possible_day = days_active if params["recency_bias"] > 0.5 else int(days_active * params["recency_bias"] * 1.5)
        last_possible_day = max(min(last_possible_day, days_active), 1)

        order_days = np.sort(np.random.choice(range(1, last_possible_day + 1), size=min(n_orders, last_possible_day), replace=False)) \
            if n_orders > 0 else []

        for d in order_days:
            order_date = cust["signup_date"] + timedelta(days=int(d))
            if order_date > END_DATE:
                continue
            n_items = np.random.randint(1, 5)
            chosen = np.random.choice(len(products), size=n_items, replace=True)
            for pidx in chosen:
                prod = products[pidx]
                qty = np.random.randint(1, 4)
                price = prod["unit_price"] * params["aov_mult"] * np.random.uniform(0.9, 1.1)
                rows.append({
                    "order_id": f"O{order_id:07d}",
                    "customer_id": cust["customer_id"],
                    "product_id": prod["product_id"],
                    "category": prod["category"],
                    "order_date": order_date,
                    "quantity": qty,
                    "unit_price": round(price, 2),
                    "revenue": round(price * qty, 2),
                })
            order_id += 1

    tx = pd.DataFrame(rows)
    return tx


def generate_daily_product_demand(products_df):
    """Independent smooth daily demand series per product for forecasting (separate from transaction noise)."""
    dates = pd.date_range(START_DATE, END_DATE, freq="D")
    all_rows = []
    for _, prod in products_df.iterrows():
        t = np.arange(len(dates))
        trend = prod["base_daily_demand"] + prod["trend"] * t
        weekly = 1 + 0.25 * np.sin(2 * np.pi * t / 7)
        yearly = 1 + prod["seasonality_amp"] * np.sin(2 * np.pi * t / 365.25 + np.random.uniform(0, 6))
        noise = np.random.normal(0, 0.15, size=len(dates))
        demand = np.clip(trend * weekly * yearly + trend * noise, 0, None)
        demand = np.round(demand).astype(int)
        all_rows.append(pd.DataFrame({
            "date": dates,
            "product_id": prod["product_id"],
            "category": prod["category"],
            "units_sold": demand
        }))
    return pd.concat(all_rows, ignore_index=True)


def main():
    print("Generating products...")
    products_df = generate_products()

    print("Generating customers...")
    customers_df = generate_customers()

    print("Generating transactions (this may take a minute)...")
    tx_df = generate_transactions(customers_df, products_df)

    print("Generating daily product demand series...")
    demand_df = generate_daily_product_demand(products_df)

    customers_out = customers_df.drop(columns=["_behavior_seed"])

    products_df.to_csv(os.path.join(OUT_DIR, "products.csv"), index=False)
    customers_out.to_csv(os.path.join(OUT_DIR, "customers.csv"), index=False)
    tx_df.to_csv(os.path.join(OUT_DIR, "transactions.csv"), index=False)
    demand_df.to_csv(os.path.join(OUT_DIR, "daily_demand.csv"), index=False)

    print(f"Products: {len(products_df)}")
    print(f"Customers: {len(customers_out)}")
    print(f"Transactions (line items): {len(tx_df)}")
    print(f"Daily demand rows: {len(demand_df)}")
    print("Saved to", OUT_DIR)


if __name__ == "__main__":
    main()
