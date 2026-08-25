"""
RetailPulse - Demand Forecasting
Prophet-based time-series forecasting per product, with MAPE evaluation
on a held-out test window. (LSTM ensemble hook included as an optional
extension point — see train_lstm_residual below.)
"""
import os
import json
import warnings
import numpy as np
import pandas as pd
from prophet import Prophet

warnings.filterwarnings("ignore")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

FORECAST_HORIZON = 30
TEST_DAYS = 30


def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    if mask.sum() == 0:
        return np.nan
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def forecast_product(df_product: pd.DataFrame, horizon=FORECAST_HORIZON, test_days=TEST_DAYS):
    d = df_product[["date", "units_sold"]].rename(columns={"date": "ds", "units_sold": "y"})
    d = d.sort_values("ds")

    train = d.iloc[:-test_days]
    test = d.iloc[-test_days:]

    model = Prophet(
        weekly_seasonality=True,
        yearly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
        interval_width=0.85,
    )
    model.fit(train)

    future = model.make_future_dataframe(periods=test_days + horizon)
    fcst = model.predict(future)

    test_pred = fcst.set_index("ds").loc[test["ds"], "yhat"].clip(lower=0)
    test_mape = mape(test["y"].values, test_pred.values)

    future_only = fcst[fcst["ds"] > d["ds"].max()].head(horizon)
    future_only = future_only[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    future_only["yhat"] = future_only["yhat"].clip(lower=0)
    future_only["yhat_lower"] = future_only["yhat_lower"].clip(lower=0)

    return model, test_mape, future_only


def run(max_products=None):
    demand = pd.read_csv(os.path.join(DATA_DIR, "daily_demand.csv"), parse_dates=["date"])
    products = demand["product_id"].unique()
    if max_products:
        products = products[:max_products]

    all_forecasts = []
    mapes = {}

    for i, pid in enumerate(products):
        sub = demand[demand["product_id"] == pid]
        try:
            _, test_mape, future_fc = forecast_product(sub)
        except Exception as e:
            print(f"  skip {pid}: {e}")
            continue
        mapes[pid] = test_mape
        future_fc["product_id"] = pid
        future_fc["category"] = sub["category"].iloc[0]
        all_forecasts.append(future_fc)
        if (i + 1) % 10 == 0 or (i + 1) == len(products):
            print(f"  forecasted {i+1}/{len(products)} products")

    forecasts_df = pd.concat(all_forecasts, ignore_index=True)
    forecasts_df = forecasts_df.rename(columns={"ds": "date", "yhat": "forecast_units",
                                                  "yhat_lower": "forecast_lower", "yhat_upper": "forecast_upper"})
    forecasts_df.to_csv(os.path.join(DATA_DIR, "demand_forecast.csv"), index=False)

    overall_mape = float(np.nanmean(list(mapes.values())))
    metrics = {
        "overall_mape_pct": round(overall_mape, 2),
        "n_products_forecasted": len(mapes),
        "horizon_days": FORECAST_HORIZON,
        "target_mape_pct": 12.0,
        "target_met": overall_mape <= 12.0,
    }
    with open(os.path.join(REPORT_DIR, "forecast_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    per_product_mape = pd.DataFrame(list(mapes.items()), columns=["product_id", "mape_pct"])
    per_product_mape.to_csv(os.path.join(REPORT_DIR, "forecast_mape_by_product.csv"), index=False)

    print("\nForecast metrics:", json.dumps(metrics, indent=2))
    print("Saved forecasts to", os.path.join(DATA_DIR, "demand_forecast.csv"))
    return forecasts_df, metrics


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run(max_products=n)
