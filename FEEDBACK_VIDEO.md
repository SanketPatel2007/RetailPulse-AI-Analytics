# Feedback Video — Recording Guide

Note: the Zidio brief document I have doesn't list a "feedback video" as one of the five
mandatory deliverables (it lists Report, Live Demo, GitHub repo, README, Demo video). If your
program is asking for this separately — e.g. a mentor/peer feedback session, or a self-review —
here's a guide for the two most common versions. Adjust to whichever your program actually
requested.

---

## Version A — Self-Reflection / Retrospective Video (most common ask)
A short video of you talking through what worked, what didn't, and what you'd change — a spoken
version of the "Personal Reflection" section in the Project Report.

**Suggested script (~2–3 minutes):**

1. **What I built** (20s) — one-sentence recap of RetailPulse.
2. **What worked well** (40s) — e.g. "The segmentation cleanly separated into 7 business-meaningful
   groups without much tuning, and the SHAP explainability made the churn model's decisions
   genuinely inspectable rather than a black box."
3. **What was hardest** (40s) — e.g. "Getting an honest churn AUC took catching a label-leakage
   bug — my first version scored 0.95 AUC because I accidentally let the model see the future.
   Fixing the time split brought it down to a more believable 0.80, which was the right number,
   even though it looked worse."
4. **What I'd do differently / next** (40s) — e.g. "I'd add the LSTM ensemble leg to close the
   forecast MAPE gap, and wire in MLflow so I could compare runs instead of eyeballing JSON files."
5. **Close** (10s) — thank the reviewer, point to the report/repo for detail.

## Version B — Feedback *Received* From a Mentor/Peer (if that's what's meant)
If this is meant to capture someone else's feedback on your work (a mentor, teammate, or peer
reviewer critiquing the project), that's not something I can generate — it requires an actual
person watching your demo and reacting. What I can do:
- Prepare a **3–5 question feedback prompt sheet** to hand your reviewer before they record, so
  their feedback is structured and useful. Want me to draft that?

---

## Recording checklist
- [ ] Keep it short and honest — genuine "what I'd change" carries more weight than a highlight reel
- [ ] Webcam or voice-over is fine; screen isn't required unless referencing the dashboard
- [ ] Upload to YouTube (unlisted), Loom, or Drive, get a shareable link

## Fill in once recorded
**Feedback video link:** `<PASTE LINK HERE ONCE RECORDED>`
**Version used:** ☐ A — Self-reflection ☐ B — Mentor/peer feedback

---
*This file is a submission-tracking placeholder — replace the bracketed line above with your real video link once recorded. If your program's requirement is different from both versions above, tell me what the actual instructions say and I'll rewrite this to match exactly.*
