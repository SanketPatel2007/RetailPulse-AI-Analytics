"""
RetailPulse - Full Pipeline Runner
Runs the complete pipeline end-to-end: data generation -> segmentation ->
churn model -> demand forecasting -> inventory optimization.

Usage:
    python run_pipeline.py            # full run
    python run_pipeline.py --quick    # quick run (fewer products forecasted, for testing)
"""
import argparse
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import generate_data
import segmentation
import churn
import forecasting
import inventory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Forecast only 10 products for a fast smoke test")
    parser.add_argument("--skip-data", action="store_true", help="Skip regenerating raw data if it already exists")
    args = parser.parse_args()

    t0 = time.time()

    if not args.skip_data:
        print("\n=== STEP 1/5: Generating synthetic retail data ===")
        generate_data.main()
    else:
        print("\n=== STEP 1/5: Skipped (using existing data) ===")

    print("\n=== STEP 2/5: Customer segmentation (RFM + K-Means) ===")
    segmentation.run(k=7)

    print("\n=== STEP 3/5: Churn prediction (XGBoost + SHAP) ===")
    churn.run()

    print("\n=== STEP 4/5: Demand forecasting (Prophet) ===")
    forecasting.run(max_products=10 if args.quick else None)

    print("\n=== STEP 5/5: Inventory optimization ===")
    inventory.compute_inventory_plan()

    elapsed = time.time() - t0
    print(f"\n✅ Pipeline complete in {elapsed/60:.1f} minutes.")
    print("Launch the dashboard with:  streamlit run dashboard/app.py")


if __name__ == "__main__":
    main()
