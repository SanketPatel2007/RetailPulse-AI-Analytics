# Live Public Demo — Deployment Guide

I can't deploy this to a live URL myself (I have no ability to stand up a public server or
register a domain), but the app is already deployment-ready. Below are the two fastest paths —
both free and meet the brief's requirements (HTTPS, no VPN, no sign-up, fast load).

---

## Option A — Streamlit Community Cloud (recommended, ~5 minutes)

1. Push the project to GitHub first (see `SOURCE_CODE.md`).
2. Go to **https://share.streamlit.io** and sign in with GitHub.
3. Click **"New app"** → select your `RetailPulse` repo → branch `main`.
4. Set **Main file path** to:
   ```
   dashboard/app.py
   ```
5. Click **Deploy**. Streamlit Cloud installs `requirements.txt` automatically.
6. **Important:** the app reads pre-generated CSVs from `data/` and `reports/`. Make sure those
   folders (with their CSV/JSON contents) are committed to the repo — don't `.gitignore` them,
   since Streamlit Cloud won't run `run_pipeline.py` for you automatically. If you'd rather
   generate fresh data on startup, add this to the top of `dashboard/app.py`:
   ```python
   import os, subprocess
   if not os.path.exists("data/inventory_plan.csv"):
       subprocess.run(["python", "run_pipeline.py", "--quick"], check=True)
   ```
   (use `--quick` so cold-start deploys finish in under a minute; drop it once you have a paid
   tier or don't mind a ~3 minute first load)
7. You'll get a URL like `https://retailpulse-<random>.streamlit.app` — that's your live link.

## Option B — Hugging Face Spaces

1. Create a new Space at **https://huggingface.co/new-space**, SDK = **Streamlit**.
2. Upload the full `retailpulse/` folder contents (or connect the GitHub repo via Space settings).
3. Set the Space's app file to `dashboard/app.py` in the Space settings if it's not auto-detected.
4. The Space builds automatically; URL format: `https://huggingface.co/spaces/<you>/retailpulse`.

## Pre-flight checklist (per the brief's Live Demo Requirements)
- [ ] Publicly accessible, no VPN/geo-restriction
- [ ] HTTPS enforced (both options above provide this by default)
- [ ] Core functionality works without sign-up (this dashboard has none — good by default)
- [ ] Initial load under 8 seconds — test after deploy; if slow, commit pre-generated `data/`
      and `reports/` folders rather than regenerating on startup
- [ ] Add a one-line instruction banner at the top of the dashboard if anything is non-obvious
      (e.g. "Select a product from the sidebar to see its forecast")

---

## Fill in once deployed
**Live demo URL:** `<PASTE LINK HERE ONCE DEPLOYED>`

**Platform used:** ☐ Streamlit Community Cloud ☐ Hugging Face Spaces ☐ AWS ☐ GCP ☐ Other: ______

---
*This file is a submission-tracking placeholder — replace the bracketed line above with your real live URL once deployed.*
