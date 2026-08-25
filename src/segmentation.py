"""
RetailPulse - Customer Segmentation
RFM (Recency, Frequency, Monetary) feature engineering + K-Means clustering.
"""
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def build_rfm(tx_df: pd.DataFrame, snapshot_date=None) -> pd.DataFrame:
    tx_df["order_date"] = pd.to_datetime(tx_df["order_date"])
    if snapshot_date is None:
        snapshot_date = tx_df["order_date"].max() + pd.Timedelta(days=1)

    rfm = tx_df.groupby("customer_id").agg(
        recency=("order_date", lambda x: (snapshot_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum"),
        avg_order_value=("revenue", "mean"),
        total_items=("quantity", "sum"),
        distinct_categories=("category", "nunique"),
        first_purchase=("order_date", "min"),
        last_purchase=("order_date", "max"),
    ).reset_index()

    rfm["tenure_days"] = (snapshot_date - rfm["first_purchase"]).dt.days
    return rfm


def score_rfm(rfm: pd.DataFrame) -> pd.DataFrame:
    rfm = rfm.copy()
    rfm["R_score"] = pd.qcut(rfm["recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]
    return rfm


def cluster_customers(rfm: pd.DataFrame, k=7, random_state=42):
    features = ["recency", "frequency", "monetary", "avg_order_value", "tenure_days"]
    X = rfm[features].copy()
    X["monetary"] = np.log1p(X["monetary"])
    X["avg_order_value"] = np.log1p(X["avg_order_value"])
    X["frequency"] = np.log1p(X["frequency"])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    labels = km.fit_predict(X_scaled)
    rfm["cluster"] = labels

    sil = silhouette_score(X_scaled, labels)
    return rfm, km, scaler, sil


def label_segments(rfm: pd.DataFrame) -> pd.DataFrame:
    """Assign human-readable business labels to clusters based on their RFM profile."""
    profile = rfm.groupby("cluster")[["recency", "frequency", "monetary"]].mean()
    profile["r_rank"] = profile["recency"].rank()          # low recency (recent) = low rank = good
    profile["f_rank"] = profile["frequency"].rank(ascending=False)
    profile["m_rank"] = profile["monetary"].rank(ascending=False)
    profile["score"] = profile["r_rank"] + profile["f_rank"] + profile["m_rank"]

    ordered_clusters = profile.sort_values("score").index.tolist()
    n = len(ordered_clusters)

    label_pool = ["Champions", "Loyal Customers", "Potential Loyalists", "Promising",
                  "Needs Attention", "At Risk", "Hibernating", "Lost"]
    labels_assigned = label_pool[:n] if n <= len(label_pool) else label_pool + [f"Segment {i}" for i in range(n - len(label_pool))]

    cluster_to_label = {cl: labels_assigned[i] for i, cl in enumerate(ordered_clusters)}
    rfm["segment"] = rfm["cluster"].map(cluster_to_label)
    return rfm


def run(k=7):
    tx = pd.read_csv(os.path.join(DATA_DIR, "transactions.csv"))
    rfm = build_rfm(tx)
    rfm = score_rfm(rfm)
    rfm, km, scaler, sil = cluster_customers(rfm, k=k)
    rfm = label_segments(rfm)

    out_path = os.path.join(DATA_DIR, "customer_segments.csv")
    rfm.to_csv(out_path, index=False)

    print(f"Silhouette score: {sil:.3f}")
    print(rfm["segment"].value_counts())
    print("Saved segments to", out_path)
    return rfm


if __name__ == "__main__":
    run()
