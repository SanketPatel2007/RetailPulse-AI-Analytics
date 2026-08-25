"""
RetailPulse - Interactive Analytics Dashboard
Run with: streamlit run dashboard/app.py
"""
import os
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

st.set_page_config(
    page_title="RetailPulse Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- THEME ----------
PRIMARY = "#3B4C9E"      # deep indigo (Zidio brand-adjacent)
ACCENT = "#2CA58D"       # teal-green
WARN = "#E0A458"
DANGER = "#D64545"
BG = "#F7F8FC"

st.markdown(f"""
<style>
    .main {{ background-color: {BG}; }}
    .metric-card {{
        background: white; border-radius: 12px; padding: 1.1rem 1.3rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08); border-left: 4px solid {PRIMARY};
    }}
    h1, h2, h3 {{ color: #1E2749; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    d = {}
    d["products"] = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
    d["customers"] = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"), parse_dates=["signup_date"])
    d["transactions"] = pd.read_csv(os.path.join(DATA_DIR, "transactions.csv"), parse_dates=["order_date"])
    d["daily_demand"] = pd.read_csv(os.path.join(DATA_DIR, "daily_demand.csv"), parse_dates=["date"])
    d["segments"] = pd.read_csv(os.path.join(DATA_DIR, "customer_segments.csv"))
    d["churn_scores"] = pd.read_csv(os.path.join(DATA_DIR, "churn_scores.csv"))
    d["forecast"] = pd.read_csv(os.path.join(DATA_DIR, "demand_forecast.csv"), parse_dates=["date"])
    d["inventory"] = pd.read_csv(os.path.join(DATA_DIR, "inventory_plan.csv"))
    return d


@st.cache_data
def load_metrics():
    m = {}
    for name in ["churn_metrics", "forecast_metrics", "inventory_summary"]:
        path = os.path.join(REPORT_DIR, f"{name}.json")
        if os.path.exists(path):
            with open(path) as f:
                m[name] = json.load(f)
    return m


data = load_data()
metrics = load_metrics()

# ---------- SIDEBAR ----------
st.sidebar.markdown("## 📊 RetailPulse")
st.sidebar.caption("AI-Powered Customer Analytics & Demand Forecasting")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview", "👥 Customer Segmentation", "⚠️ Churn Risk",
     "📈 Demand Forecasting", "📦 Inventory Optimization"],
)
st.sidebar.divider()
st.sidebar.markdown("**Data window**")
st.sidebar.write(f"{data['transactions']['order_date'].min().date()} → {data['transactions']['order_date'].max().date()}")
st.sidebar.markdown("**Scale**")
st.sidebar.write(f"{data['customers'].shape[0]:,} customers · {data['products'].shape[0]} products")
st.sidebar.write(f"{data['transactions'].shape[0]:,} line items")

# ============================================================
# OVERVIEW
# ============================================================
if page == "🏠 Overview":
    st.title("RetailPulse — Executive Overview")
    st.caption("End-to-end retail analytics: demand forecasting, segmentation, churn, and inventory in one view.")

    tx = data["transactions"]
    total_revenue = tx["revenue"].sum()
    active_customers = tx["customer_id"].nunique()
    high_risk = (data["churn_scores"]["risk_tier"] == "High").sum()
    reorder_now = data["inventory"]["needs_reorder_now"].sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Active Customers", f"{active_customers:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("High Churn-Risk Customers", f"{high_risk:,}",
                   delta=f"{high_risk/active_customers*100:.1f}% of base", delta_color="inverse")
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Products Needing Reorder", f"{reorder_now}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Revenue Trend")
        rev_daily = tx.groupby(tx["order_date"].dt.to_period("W"))["revenue"].sum().reset_index()
        rev_daily["order_date"] = rev_daily["order_date"].dt.to_timestamp()
        fig = px.line(rev_daily, x="order_date", y="revenue", color_discrete_sequence=[PRIMARY])
        fig.update_layout(height=350, margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Revenue by Category")
        cat_rev = tx.groupby("category")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
        fig = px.pie(cat_rev, names="category", values="revenue", hole=0.5,
                     color_discrete_sequence=px.colors.sequential.Teal)
        fig.update_layout(height=350, margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Model Performance Summary")
    m1, m2, m3 = st.columns(3)
    if "churn_metrics" in metrics:
        with m1:
            st.info(f"**Churn Model**\n\nAUC-ROC: {metrics['churn_metrics']['auc_roc']}\n\n"
                    f"Precision@Top20%: {metrics['churn_metrics']['precision_at_top20pct']}")
    if "forecast_metrics" in metrics:
        with m2:
            fm = metrics["forecast_metrics"]
            st.info(f"**Demand Forecast**\n\nMAPE: {fm['overall_mape_pct']}%\n\n"
                    f"Target ≤12%: {'✅ Met' if fm['target_met'] else '⚠️ Above target'}")
    if "inventory_summary" in metrics:
        with m3:
            im = metrics["inventory_summary"]
            st.info(f"**Inventory**\n\n{im['n_high_stockout_risk']} high stockout-risk SKUs\n\n"
                    f"{im['total_recommended_units_to_order']:,} units recommended to order")

# ============================================================
# CUSTOMER SEGMENTATION
# ============================================================
elif page == "👥 Customer Segmentation":
    st.title("Customer Segmentation (RFM + K-Means)")
    seg = data["segments"]

    c1, c2 = st.columns([1, 1.3])
    with c1:
        st.subheader("Segment Sizes")
        counts = seg["segment"].value_counts().reset_index()
        counts.columns = ["segment", "count"]
        fig = px.bar(counts, x="count", y="segment", orientation="h",
                     color="count", color_continuous_scale="Tealgrn")
        fig.update_layout(height=400, margin=dict(t=10, l=10, r=10, b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Recency vs. Frequency vs. Monetary")
        fig = px.scatter(seg, x="recency", y="frequency", size="monetary", color="segment",
                          hover_data=["customer_id"], size_max=35)
        fig.update_layout(height=400, margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Segment Profiles")
    profile = seg.groupby("segment").agg(
        customers=("customer_id", "count"),
        avg_recency_days=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        avg_order_value=("avg_order_value", "mean"),
    ).round(1).sort_values("avg_monetary", ascending=False)
    st.dataframe(profile, use_container_width=True)

    st.subheader("Explore a Segment")
    chosen_seg = st.selectbox("Segment", seg["segment"].unique())
    st.dataframe(
        seg[seg["segment"] == chosen_seg][
            ["customer_id", "recency", "frequency", "monetary", "avg_order_value", "RFM_score"]
        ].sort_values("monetary", ascending=False).head(50),
        use_container_width=True,
    )

# ============================================================
# CHURN RISK
# ============================================================
elif page == "⚠️ Churn Risk":
    st.title("Churn Risk Analysis")
    churn = data["churn_scores"]

    c1, c2, c3 = st.columns(3)
    for col, tier, color in zip([c1, c2, c3], ["Low", "Medium", "High"], [ACCENT, WARN, DANGER]):
        n = (churn["risk_tier"] == tier).sum()
        with col:
            st.markdown(f'<div class="metric-card" style="border-left-color:{color}">', unsafe_allow_html=True)
            st.metric(f"{tier} Risk", f"{n:,}", f"{n/len(churn)*100:.1f}% of customers")
            st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    col1, col2 = st.columns([1, 1.4])
    with col1:
        st.subheader("Risk Distribution")
        fig = px.histogram(churn, x="churn_probability", nbins=30, color_discrete_sequence=[PRIMARY])
        fig.update_layout(height=350, margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top Churn Drivers (SHAP)")
        fi_path = os.path.join(REPORT_DIR, "churn_feature_importance.csv")
        if os.path.exists(fi_path):
            fi = pd.read_csv(fi_path).head(8)
            fig = px.bar(fi, x="mean_abs_shap", y="feature", orientation="h",
                         color="mean_abs_shap", color_continuous_scale="Sunsetdark")
            fig.update_layout(height=350, margin=dict(t=10, l=10, r=10, b=10), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Highest Risk Customers (prioritize for retention outreach)")
    top_risk = churn.sort_values("churn_probability", ascending=False).head(100)
    st.dataframe(top_risk, use_container_width=True)

    csv = top_risk.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export high-risk customer list (CSV)", csv, "high_risk_customers.csv", "text/csv")

# ============================================================
# DEMAND FORECASTING
# ============================================================
elif page == "📈 Demand Forecasting":
    st.title("Demand Forecasting")
    fc = data["forecast"]
    hist = data["daily_demand"]

    products = sorted(fc["product_id"].unique())
    col_a, col_b = st.columns([1, 3])
    with col_a:
        selected_product = st.selectbox("Select product", products)
        cat = fc[fc["product_id"] == selected_product]["category"].iloc[0]
        st.caption(f"Category: {cat}")

        mape_path = os.path.join(REPORT_DIR, "forecast_mape_by_product.csv")
        if os.path.exists(mape_path):
            mape_df = pd.read_csv(mape_path)
            row = mape_df[mape_df["product_id"] == selected_product]
            if not row.empty:
                st.metric("Product MAPE", f"{row['mape_pct'].iloc[0]:.1f}%")

    with col_b:
        h = hist[hist["product_id"] == selected_product].tail(90)
        f = fc[fc["product_id"] == selected_product]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=h["date"], y=h["units_sold"], name="Historical",
                                  line=dict(color=PRIMARY)))
        fig.add_trace(go.Scatter(x=f["date"], y=f["forecast_units"], name="Forecast",
                                  line=dict(color=ACCENT, dash="dash")))
        fig.add_trace(go.Scatter(
            x=pd.concat([f["date"], f["date"][::-1]]),
            y=pd.concat([f["forecast_upper"], f["forecast_lower"][::-1]]),
            fill="toself", fillcolor="rgba(44,165,141,0.15)", line=dict(color="rgba(0,0,0,0)"),
            name="Confidence Interval", showlegend=True,
        ))
        fig.update_layout(height=420, margin=dict(t=20, l=10, r=10, b=10),
                           title=f"30-Day Demand Forecast — {selected_product}")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("What-If: Adjust Demand Assumption")
    adj = st.slider("Apply demand multiplier (e.g. promotion or seasonality shock)", 0.5, 2.0, 1.0, 0.05)
    adj_forecast = f.copy()
    adj_forecast["adjusted_units"] = adj_forecast["forecast_units"] * adj
    fig2 = px.bar(adj_forecast, x="date", y="adjusted_units", color_discrete_sequence=[WARN])
    fig2.update_layout(height=300, margin=dict(t=10, l=10, r=10, b=10),
                        title=f"Adjusted forecast (×{adj})  —  30-day total: {adj_forecast['adjusted_units'].sum():.0f} units")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Category-Level Forecast Summary")
    cat_summary = fc.groupby("category")["forecast_units"].sum().reset_index().sort_values("forecast_units", ascending=False)
    fig3 = px.bar(cat_summary, x="category", y="forecast_units", color="category",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig3.update_layout(height=350, margin=dict(t=10, l=10, r=10, b=10), showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# INVENTORY OPTIMIZATION
# ============================================================
elif page == "📦 Inventory Optimization":
    st.title("Inventory Optimization")
    inv = data["inventory"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SKUs needing reorder", int(inv["needs_reorder_now"].sum()))
    c2.metric("High stockout risk", int((inv["stockout_risk"] == "High").sum()))
    c3.metric("High overstock risk", int((inv["overstock_risk"] == "High").sum()))
    c4.metric("Units recommended to order", f"{inv['recommended_order_qty'].sum():,.0f}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Stockout Risk by Category")
        risk_ct = inv.groupby(["category", "stockout_risk"]).size().reset_index(name="count")
        fig = px.bar(risk_ct, x="category", y="count", color="stockout_risk",
                     color_discrete_map={"Low": ACCENT, "Medium": WARN, "High": DANGER})
        fig.update_layout(height=380, margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Current Stock vs. Reorder Point")
        fig = px.scatter(inv, x="reorder_point", y="current_stock", color="stockout_risk",
                          hover_data=["product_id", "category"],
                          color_discrete_map={"Low": ACCENT, "Medium": WARN, "High": DANGER})
        max_v = max(inv["reorder_point"].max(), inv["current_stock"].max())
        fig.add_shape(type="line", x0=0, y0=0, x1=max_v, y1=max_v, line=dict(dash="dot", color="gray"))
        fig.update_layout(height=380, margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Reorder Recommendations")
    filt = st.multiselect("Filter by stockout risk", ["High", "Medium", "Low"], default=["High", "Medium"])
    filtered = inv[inv["stockout_risk"].isin(filt)].sort_values("recommended_order_qty", ascending=False)
    st.dataframe(filtered, use_container_width=True)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export reorder plan (CSV)", csv, "inventory_reorder_plan.csv", "text/csv")

st.sidebar.divider()
st.sidebar.caption("RetailPulse v2.0 · Zidio Development · March 2026")
