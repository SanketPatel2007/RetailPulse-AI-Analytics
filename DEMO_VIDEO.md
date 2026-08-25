# Demo Video — Recording Guide (4–8 minutes, per brief)

I can't record video or narrate a screen capture myself, but here's a tight script mapped to
what's actually in the dashboard, so recording is just "follow this and press record" — free
tools: **Loom** (easiest, auto-uploads and gives you a shareable link) or **OBS Studio** +
manual YouTube upload (unlisted).

---

## Script (~6 minutes)

**0:00 – 0:30 | Intro**
> "This is RetailPulse, an AI-powered customer analytics and demand forecasting platform I
> built for Zidio Development. It takes raw retail sales, customer, and inventory data and
> produces four things: demand forecasts, customer segments, churn risk scores, and inventory
> reorder recommendations — all in one dashboard."

**0:30 – 1:15 | Overview page**
- Open the dashboard, land on **🏠 Overview**.
- Point out: total revenue, active customers, high-risk customer count, products needing reorder.
- Scroll to the revenue trend chart and category breakdown.
- Mention the model performance summary cards at the bottom (churn AUC, forecast MAPE, inventory risk).

**1:15 – 2:15 | Customer Segmentation**
- Switch to **👥 Customer Segmentation**.
- Show the segment size bar chart — explain RFM (Recency, Frequency, Monetary) briefly.
- Point at the RFM scatter plot — bubble size = spend.
- Select a segment from the dropdown (e.g. "At Risk") and show the underlying customer table.

**2:15 – 3:15 | Churn Risk**
- Switch to **⚠️ Churn Risk**.
- Show the Low/Medium/High risk tier cards.
- Point at the churn probability histogram.
- Show the SHAP feature importance chart — explain that frequency and recency are the top drivers.
- Scroll to the high-risk customer table and click the CSV export button.

**3:15 – 4:30 | Demand Forecasting**
- Switch to **📈 Demand Forecasting**.
- Pick a product from the dropdown, show the historical + forecast chart with confidence interval.
- Move the **what-if slider** (demand multiplier) and show the adjusted forecast chart update live —
  this is a good moment to say "if marketing runs a promotion, this shows the inventory impact instantly."
- Show the category-level forecast summary chart.

**4:30 – 5:30 | Inventory Optimization**
- Switch to **📦 Inventory Optimization**.
- Show the four summary metrics (SKUs needing reorder, stockout risk, overstock risk, units to order).
- Point at the stockout-risk-by-category chart and the current-stock-vs-reorder-point scatter.
- Filter the reorder table by risk tier, export the CSV.

**5:30 – 6:00 | Close**
> "Under the hood: customer segmentation uses RFM plus K-Means, churn uses XGBoost with SHAP
> explainability and a leak-safe time-based evaluation split, demand forecasting uses Prophet
> per product, and inventory recommendations come from a standard safety-stock formula. Full
> source, report, and metrics are in the linked repo. Thanks for watching."

---

## Recording checklist
- [ ] Record at 1080p minimum, browser window maximized
- [ ] Test audio levels before the real take
- [ ] Keep it 4–8 minutes (per brief)
- [ ] Upload to YouTube (unlisted) or Loom, get a shareable link
- [ ] Verify the link works in a private/incognito browser window before submitting

## Fill in once recorded
**Demo video link:** `<PASTE LINK HERE ONCE RECORDED>`

---
*This file is a submission-tracking placeholder — replace the bracketed line above with your real video link once recorded.*
