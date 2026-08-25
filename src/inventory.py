"""
RetailPulse - Inventory Optimization
Uses forecasted demand + lead time + demand variability to recommend
safety stock, reorder points, and reorder quantities per product.

Reorder Point (ROP) = (avg daily demand x lead time) + safety stock
Safety Stock = Z * std_dev(daily demand) * sqrt(lead_time)
Recommended Order Qty = target coverage days x avg daily demand - current stock (floored at 0)
"""
import os
import json
import numpy as np
import pandas as pd
from scipy.stats import norm

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

SERVICE_LEVEL = 0.95          # -> Z ~ 1.645
TARGET_COVERAGE_DAYS = 21


def compute_inventory_plan():
    products = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
    forecast = pd.read_csv(os.path.join(DATA_DIR, "demand_forecast.csv"), parse_dates=["date"])
    history = pd.read_csv(os.path.join(DATA_DIR, "daily_demand.csv"), parse_dates=["date"])

    z = norm.ppf(SERVICE_LEVEL)

    rows = []
    for _, prod in products.iterrows():
        pid = prod["product_id"]
        lead_time = prod["lead_time_days"]
        current_stock = prod["current_stock"]

        hist_p = history[history["product_id"] == pid]["units_sold"]
        fc_p = forecast[forecast["product_id"] == pid]

        if fc_p.empty:
            continue

        avg_daily_demand = fc_p["forecast_units"].mean()
        std_daily_demand = hist_p.std() if len(hist_p) > 1 else fc_p["forecast_units"].std()
        std_daily_demand = 0 if np.isnan(std_daily_demand) else std_daily_demand

        safety_stock = z * std_daily_demand * np.sqrt(lead_time)
        reorder_point = avg_daily_demand * lead_time + safety_stock
        target_stock = avg_daily_demand * TARGET_COVERAGE_DAYS + safety_stock

        recommended_order_qty = max(target_stock - current_stock, 0)
        needs_reorder_now = current_stock <= reorder_point

        days_of_cover_remaining = current_stock / avg_daily_demand if avg_daily_demand > 0 else np.inf
        forecast_30d_demand = fc_p["forecast_units"].sum()

        stockout_risk = "High" if current_stock < forecast_30d_demand * 0.5 else \
                         "Medium" if current_stock < forecast_30d_demand else "Low"
        overstock_risk = "High" if current_stock > forecast_30d_demand * 2.5 else \
                          "Medium" if current_stock > forecast_30d_demand * 1.8 else "Low"

        rows.append({
            "product_id": pid,
            "category": prod["category"],
            "current_stock": current_stock,
            "avg_daily_demand": round(avg_daily_demand, 2),
            "forecast_30d_demand": round(forecast_30d_demand, 1),
            "lead_time_days": lead_time,
            "safety_stock": round(safety_stock, 1),
            "reorder_point": round(reorder_point, 1),
            "recommended_order_qty": round(recommended_order_qty, 0),
            "needs_reorder_now": needs_reorder_now,
            "days_of_cover_remaining": round(days_of_cover_remaining, 1) if np.isfinite(days_of_cover_remaining) else None,
            "stockout_risk": stockout_risk,
            "overstock_risk": overstock_risk,
        })

    plan = pd.DataFrame(rows)
    plan.to_csv(os.path.join(DATA_DIR, "inventory_plan.csv"), index=False)

    summary = {
        "n_products": len(plan),
        "n_need_reorder_now": int(plan["needs_reorder_now"].sum()),
        "n_high_stockout_risk": int((plan["stockout_risk"] == "High").sum()),
        "n_high_overstock_risk": int((plan["overstock_risk"] == "High").sum()),
        "total_recommended_units_to_order": int(plan["recommended_order_qty"].sum()),
    }
    with open(os.path.join(REPORT_DIR, "inventory_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print("Saved inventory plan to", os.path.join(DATA_DIR, "inventory_plan.csv"))
    return plan


if __name__ == "__main__":
    compute_inventory_plan()
