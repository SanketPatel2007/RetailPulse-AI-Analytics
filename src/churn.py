"""
RetailPulse - Churn Prediction
XGBoost classifier to identify at-risk customers, with SHAP explainability.
Churn label definition: customer has NOT purchased in the last 90 days
relative to the dataset's snapshot date (i.e. recency > 90 days), evaluated
on data as of 90 days before the true max date so we have "future" ground truth.
"""
import os
import json
import numpy as np
import pandas as pd
import xgboost as xgb
import shap
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score, classification_report

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

CHURN_WINDOW_DAYS = 90


def build_features_and_labels(tx: pd.DataFrame, customers: pd.DataFrame):
    tx["order_date"] = pd.to_datetime(tx["order_date"])
    max_date = tx["order_date"].max()

    # Split timeline: features computed up to cutoff, label = did they churn after cutoff
    cutoff = max_date - pd.Timedelta(days=CHURN_WINDOW_DAYS)

    hist = tx[tx["order_date"] <= cutoff]
    future = tx[tx["order_date"] > cutoff]

    feat = hist.groupby("customer_id").agg(
        recency=("order_date", lambda x: (cutoff - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum"),
        avg_order_value=("revenue", "mean"),
        total_items=("quantity", "sum"),
        distinct_categories=("category", "nunique"),
        first_purchase=("order_date", "min"),
    ).reset_index()
    feat["tenure_days"] = (cutoff - feat["first_purchase"]).dt.days
    feat = feat.drop(columns=["first_purchase"])

    customers_slim = customers[["customer_id", "age", "city_tier", "acquisition_channel"]]
    feat = feat.merge(customers_slim, on="customer_id", how="left")

    active_after = set(future["customer_id"].unique())
    feat["churned"] = (~feat["customer_id"].isin(active_after)).astype(int)

    feat = pd.get_dummies(feat, columns=["city_tier", "acquisition_channel"], drop_first=True)
    return feat


def train_churn_model(feat: pd.DataFrame):
    drop_cols = ["customer_id", "churned"]
    X = feat.drop(columns=drop_cols)
    y = feat["churned"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scale_pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)

    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        scale_pos_weight=scale_pos_weight,
        eval_metric="auc",
        random_state=42,
    )
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    preds = (proba >= 0.5).astype(int)

    auc = roc_auc_score(y_test, proba)

    top20_n = max(int(len(y_test) * 0.2), 1)
    top20_idx = np.argsort(-proba)[:top20_n]
    precision_at_top20 = y_test.values[top20_idx].mean()

    metrics = {
        "auc_roc": round(float(auc), 4),
        "precision_at_top20pct": round(float(precision_at_top20), 4),
        "churn_rate_in_data": round(float(y.mean()), 4),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }

    print("Churn model metrics:", json.dumps(metrics, indent=2))
    print(classification_report(y_test, preds))

    model.save_model(os.path.join(MODEL_DIR, "churn_xgb.json"))
    with open(os.path.join(REPORT_DIR, "churn_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    # SHAP explainability
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test.iloc[:500])
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    importance = pd.DataFrame({
        "feature": X_test.columns,
        "mean_abs_shap": mean_abs_shap
    }).sort_values("mean_abs_shap", ascending=False)
    importance.to_csv(os.path.join(REPORT_DIR, "churn_feature_importance.csv"), index=False)
    print("\nTop churn drivers (SHAP):")
    print(importance.head(8).to_string(index=False))

    return model, X.columns.tolist(), metrics


def score_all_customers(model, feature_cols, feat_current: pd.DataFrame):
    """Score current (live) customers with the trained model for the dashboard."""
    X = feat_current.reindex(columns=feature_cols, fill_value=0)
    proba = model.predict_proba(X)[:, 1]
    out = feat_current[["customer_id"]].copy()
    out["churn_probability"] = proba
    out["risk_tier"] = pd.cut(
        proba, bins=[-0.01, 0.3, 0.6, 1.01], labels=["Low", "Medium", "High"]
    )
    return out


def run():
    tx = pd.read_csv(os.path.join(DATA_DIR, "transactions.csv"))
    customers = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))

    feat = build_features_and_labels(tx, customers)
    model, feature_cols, metrics = train_churn_model(feat)

    # Score using ALL history (as of latest date) for live dashboard risk scores
    tx["order_date"] = pd.to_datetime(tx["order_date"])
    max_date = tx["order_date"].max()
    live_feat = tx.groupby("customer_id").agg(
        recency=("order_date", lambda x: (max_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum"),
        avg_order_value=("revenue", "mean"),
        total_items=("quantity", "sum"),
        distinct_categories=("category", "nunique"),
        first_purchase=("order_date", "min"),
    ).reset_index()
    live_feat["tenure_days"] = (max_date - live_feat["first_purchase"]).dt.days
    live_feat = live_feat.drop(columns=["first_purchase"])
    customers_slim = customers[["customer_id", "age", "city_tier", "acquisition_channel"]]
    live_feat = live_feat.merge(customers_slim, on="customer_id", how="left")
    live_feat = pd.get_dummies(live_feat, columns=["city_tier", "acquisition_channel"], drop_first=True)

    scores = score_all_customers(model, feature_cols, live_feat)
    scores.to_csv(os.path.join(DATA_DIR, "churn_scores.csv"), index=False)
    print("\nSaved live churn scores for", len(scores), "customers")

    return model, metrics


if __name__ == "__main__":
    run()
