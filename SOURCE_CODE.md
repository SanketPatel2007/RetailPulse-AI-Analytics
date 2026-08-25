# Source Code — Submission Info

## What you already have
The full working source code is in `retailpulse_project.zip` (delivered earlier in this
conversation). It contains:

```
retailpulse/
├── data/            # generated datasets (CSV)
├── models/          # trained churn model artifact
├── reports/         # metrics JSON + SHAP importances + charts
├── src/              # generate_data.py, segmentation.py, churn.py, forecasting.py, inventory.py
├── dashboard/app.py  # Streamlit dashboard
├── run_pipeline.py   # one-command full pipeline
├── requirements.txt
└── README.md
```

This satisfies deliverable **#3 (GitHub Repository)** and **#4 (README.md)** from the Zidio
submission checklist — you just need to get it onto GitHub. There's no Figma file for this
project since it's a data/ML platform, not a UI-design deliverable; the "design" artifact here
is the Streamlit dashboard itself (`dashboard/app.py`), which is the closest equivalent.

## Steps to publish it (5 minutes)

```bash
# 1. Unzip and enter the project
unzip retailpulse_project.zip
cd retailpulse

# 2. Initialize git
git init
git add .
git commit -m "feat: initial RetailPulse platform - forecasting, segmentation, churn, inventory"

# 3. Create a new repo on GitHub named:
#    RetailPulse-AI-Customer-Analytics-Demand-Forecasting
#    (matches the naming convention in the brief)

# 4. Push
git branch -M main
git remote add origin https://github.com/<your-username>/RetailPulse-AI-Customer-Analytics-Demand-Forecasting.git
git push -u origin main
```

## Before pushing, double-check (per the brief's Section 4 requirements)
- [ ] `.gitignore` excludes `__pycache__/`, `*.pyc`, and any local venv folders
- [ ] No API keys or secrets are committed (this project has none by default)
- [ ] `requirements.txt` is present and accurate
- [ ] Commit messages are semantic (`feat: ...`, `fix: ...`) if you make further changes
- [ ] Consider splitting future changes into feature branches / PRs, even solo, per the brief's guidance

## Fill in once published
**GitHub repository URL:** `<PASTE LINK HERE ONCE PUSHED>`

---
*This file is a submission-tracking placeholder — replace the bracketed line above with your real repo link before final submission.*
