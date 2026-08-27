# 🏦 CrediVex — AI Loan Underwriting Engine
>### link for the credited web site:
>#### https://credivex-loan.onrender.com

> **An interactive, full-stack loan approval platform powered by a Support Vector Classifier (SVC) with an RBF kernel, built with Flask + Vanilla JS.**
> CrediVex simulates an automated underwriting desk: applicants (or entire portfolios) go in, a calibrated probability of default comes out, and that probability drives an approve/reject decision, a risk tier, live analytics, and exportable reports.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-SVC-orange?style=flat-square&logo=scikit-learn)
![Chart.js](https://img.shields.io/badge/Chart.js-4.x-pink?style=flat-square&logo=chart.js)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📖 Table of Contents

1. [What CrediVex Does](#-what-credivex-does)
2. [How a Decision Gets Made](#-how-a-decision-gets-made)
3. [The Machine Learning Core](#-the-machine-learning-core)
4. [Why ROC-AUC Is the Core Evaluation Metric](#-why-roc-auc-is-the-core-evaluation-metric)
5. [Risk Tiers & Decision Thresholds](#-risk-tiers--decision-thresholds)
6. [Platform Tour (Features)](#-platform-tour-features)
7. [REST API Reference](#-rest-api-reference)
8. [Project Structure](#-project-structure)
9. [Tech Stack](#-tech-stack)
10. [Local Setup](#-local-setup)
11. [Deployment](#-deployment)
12. [Bulk Upload Format](#-bulk-upload-format)
13. [License](#-license)

---

## 🎯 What CrediVex Does

### 🤖 ML Model
- **Algorithm:** Support Vector Classifier (SVC) with RBF kernel
- **Accuracy:** 91.46% ROC-AUC on held-out test set
- **Pipeline:** `StandardScaler` → `SVC(kernel='rbf', C=7.308, γ=0.8, probability=True)` → Platt Scaling
- **Support Vectors:** 15,003 (Class 0: 7,440 | Class 1: 7,563)
- Evaluates **6 financial dimensions** per applicant

### 📋 Evaluation Hub
- **Single Entry** — fill in 6 fields, get instant prediction with:
  - Approval probability dial (doughnut chart)
  - Benchmark comparison bar chart
  - Risk diagnostic checklist
- **Bulk Upload (CSV/Excel)** — evaluate hundreds of applicants at once using drag-and-drop, with a live progress bar and downloadable results table
CrediVex is an end-to-end demonstration of a production-style ML underwriting pipeline: from raw applicant data, to a trained scikit-learn model, to a REST API, to a full browser dashboard.

Given six financial attributes about an applicant, CrediVex:

1. Feeds them through a trained **Support Vector Classifier (RBF kernel)**.
2. Produces a **calibrated approval probability** (not just a hard yes/no).
3. Applies a **business decision threshold** (80% confidence) to turn that probability into an Approved/Rejected verdict.
4. Buckets the applicant into a **risk tier** (Prime, Moderate, High Risk, Critical).
5. Surfaces everything — the math, the probabilities, and portfolio-level trends — through an interactive dashboard, so the model isn't a black box.

### 📥 Download Analytics & Visual Reports *(new)*
- Centralized downloads hub for all generated reports and artifacts
- Download **Excel Reports** with raw data and native Excel charts
- Download **PowerPoint Presentations** with executive summaries and CREDIVEX branding
- Download **Raw Evaluation Data** in CSV format
- Download developer models (`.pkl`) and Jupyter notebooks (`.ipynb`)

### 🛠️ Developer & SDK Page
- Live model telemetry pulled from REST API
- Downloadable `.pkl` model binary
- Copy-paste code snippets (Python, cURL, JavaScript)
It supports both **single-applicant evaluation** (a loan officer typing in one applicant's numbers) and **bulk evaluation** (uploading a CSV/Excel file of hundreds of applicants at once), plus **Excel/PowerPoint report export** of the results.

---

## 🔄 How a Decision Gets Made

```
Applicant data (6 features)
        │
        ▼
  StandardScaler            ← z-score normalization, so no single feature
        │                     (e.g. annual_income in the tens of thousands)
        ▼                     dominates the distance calculations below
  SVC (RBF kernel)
        │
        ▼
  predict_proba() → P(approved)   ← a calibrated probability between 0 and 1
        │
        ▼
  Decision threshold (≥ 0.80)  →  Approved / Rejected
        │
        ▼
  Risk tier (Prime / Moderate / High / Critical)
        │
        ▼
  Dashboard, benchmarks, charts, and Excel/PPT export
```

The model itself never outputs a flat "yes" or "no" — it outputs a probability. CrediVex deliberately separates **"how good is the model at ranking risk"** (measured by ROC-AUC, see below) from **"how conservative should the business be when converting that ranking into a decision"** (the 80% confidence cutoff). Those are two different knobs, and conflating them is a common mistake in credit-risk modeling.

---

## 🤖 The Machine Learning Core

The training process lives in `Project_Loan_final.ipynb`. Here's what it actually does, end to end:

**Data**
- Source dataset: `Loan_approval_data_2025.csv` — 50,000 applicant records, 20 raw columns.
- Only **6 features** are used for modeling: `annual_income`, `loan_amount`, `credit_score`, `debt_to_income_ratio`, `years_employed`, `delinquencies_last_2yrs`.
- Target: `loan_status` (1 = approved, 0 = rejected) — a roughly balanced split (~55% approved / 45% rejected), no missing values.
- Split 80/20 into train (40,000 rows) and a held-out test set (10,000 rows) with `random_state=42` for reproducibility.

**Pipeline**
```python
Pipeline([
    ('scaler', StandardScaler()),
    ('svc', SVC(kernel='rbf', C=7.308, gamma=0.2,
                class_weight={0: 4.2, 1: 2.2}, probability=True))
])
```

**Hyperparameter search**
- `RandomizedSearchCV` explored combinations of `C`, `gamma`, and `class_weight` using **3-fold cross-validation scored on `roc_auc`** — meaning the search wasn't optimizing for raw accuracy, it was optimizing directly for the model's ability to rank risk (see next section for why that matters).
- The search's best result landed on `C ≈ 7.31`, `gamma = 0.8`, balanced class weights, for a mean CV ROC-AUC of **≈ 0.90**.
- From there, the class weights were **manually re-tuned** to `{0: 4.2, 1: 2.2}` (rejected class weighted roughly 2× the approved class) and `gamma` was lowered to `0.2`. This is a deliberate business choice layered on top of the statistical search: it pushes the SVC's decision boundary to be more cautious about false approvals — i.e., it penalizes the model more heavily for approving someone who should have been rejected than the reverse.
- Re-validated with 3-fold CV (**mean ROC-AUC ≈ 0.92**) and confirmed on the untouched test set.

**Shipped model** (`loan_svc_project_2.pkl`, verified directly from the pickled pipeline in this repo):

| Parameter | Value |
|---|---|
| Kernel | RBF |
| `C` (regularization) | 7.308 |
| `gamma` | 0.2 |
| `class_weight` | `{0: 4.2, 1: 2.2}` |
| Total support vectors | 14,794 (5,217 from the rejected class, 9,577 from the approved class) |
| Intercept (`b`) | −1.3422 |
| Probability calibration | enabled (`probability=True`, Platt scaling) |
| Test-set ROC-AUC (last notebook run) | **0.9146** |

> **Note for maintainers:** `app.py` currently hardcodes `ROC_AUC_SCORE = 0.8977` for the `/api/metadata` endpoint, while the notebook's last saved run reports a test ROC-AUC of `0.9146` for the exact `.pkl` shipped in the repo. Worth syncing that constant to the latest notebook output (or computing it dynamically at startup) so the dashboard's displayed accuracy always matches the deployed model.

Because `probability=True` is set, `predict_proba` doesn't come straight from the SVM's raw decision function — scikit-learn fits an internal calibration (Platt/sigmoid scaling via cross-validation) on top of it, which is what turns "distance from the separating hyperplane" into an actual, usable probability like `0.956`.

---

## 📊 Why ROC-AUC Is the Core Evaluation Metric

CrediVex uses **ROC-AUC (Area Under the Receiver Operating Characteristic Curve)** as the primary yardstick for how good the model is — not accuracy, not a single confusion matrix. Here's what that means and why it's the right choice for a loan approval model specifically.

**What it measures.** For every possible probability threshold from 0 to 1, the ROC curve plots the true positive rate (approved applicants correctly identified) against the false positive rate (rejected applicants incorrectly approved). The area under that curve is a single number between 0.5 (no better than a coin flip) and 1.0 (perfect separation). Intuitively:

> **ROC-AUC = the probability that, if you pick one truly "approved" applicant and one truly "rejected" applicant at random, the model assigns a higher approval probability to the approved one.**

CrediVex's shipped model scores **≈ 0.91**, meaning it correctly ranks a random approved/rejected pair about 91% of the time.

**Why AUC and not accuracy or a fixed confusion matrix:**

- **It's threshold-independent.** CrediVex enforces an 80% confidence bar for a real approval, but that bar is a *business policy*, not a property of the model. If the business later decides to loosen the bar to 65% (to approve more applicants) or tighten it to 90% (to reduce default risk), the underlying model doesn't need to be retrained — ROC-AUC measures how good the model's *ranking* is across every possible cutoff simultaneously, so it stays valid regardless of where the threshold is set.
- **It's what the model was actually optimized for.** `RandomizedSearchCV` was configured with `scoring='roc_auc'`, so every one of the candidate hyperparameter combinations tested during training was judged and ranked by this metric — not by accuracy or F1. The hyperparameters shipped in `loan_svc_project_2.pkl` are the ones that best solved this exact objective.
- **It's resilient to the cost asymmetry in lending.** In credit risk, a false approval (giving money to someone who defaults) and a false rejection (turning away someone who would have repaid) are not equally costly, and the raw class balance can shift over time. Accuracy can look good on a lazy model that just predicts the majority class; AUC forces the model to actually separate the two outcomes across the full probability range, and pairs naturally with class-weighting techniques (like the `{0: 4.2, 1: 2.2}` weights used here) that let a business express "false approvals are worse than false rejections" without needing to hand-pick a different metric for every threshold.
- **It reflects the quality of the probability, not just the label.** Because CrediVex surfaces the raw probability everywhere (dials, benchmarks, risk tiers, bulk exports), the ranking quality behind that number matters more than any single accept/reject call. A model can get the *label* right most of the time while still being badly calibrated; AUC is sensitive to whether the model consistently scores riskier applicants lower than safer ones.

**In short:** the confusion matrix and 80%-confidence threshold you see in the app describe *one specific operating point* the business chose. ROC-AUC describes *the model itself* — how good it fundamentally is at telling good and bad credit risk apart — independent of where the business decides to draw the line.

---

## 🚦 Risk Tiers & Decision Thresholds

The live API (`app.py`) converts the model's approval probability into a decision and a risk tier as follows:

| Approval Probability | Verdict | Risk Tier |
|---|---|---|
| ≥ 80% | **Approved** | 🟢 Prime / Low Risk |
| 50% – 79% | Rejected | 🔵 Moderate / Near-Prime Risk |
| 25% – 49% | Rejected | 🟠 High Risk / Subprime |
| < 25% | Rejected | 🔴 Critical Risk / High Default Probability |

Only applicants at or above the **80% confidence bar** are approved — a deliberately conservative operating point chosen well above the model's natural 50% midpoint, consistent with the heavier class weighting placed on avoiding false approvals during training.

Each single-applicant evaluation also runs a quick benchmark check against standard underwriting heuristics (independent of the model itself), used purely to explain *why* an application looks risky:

| Metric | Safe Benchmark |
|---|---|
| Credit Score (FICO) | ≥ 670 |
| Debt-to-Income Ratio | ≤ 36% |
| Loan-to-Income Ratio | ≤ 0.40 |
| Delinquencies (last 2 yrs) | 0 |

---

## 🖥️ Platform Tour (Features)

### Overview
Landing page explaining the underwriting engine (non-linear decision margin, calibrated probabilities, standardized pipeline) and how to interpret the results.

### Model Architecture
Live view of the trained pipeline's internals, pulled straight from the loaded `.pkl` file via `/api/model-info`: kernel type, `C`/`gamma`, support-vector counts per class, intercept, and the RBF decision-function formula.

### Evaluation Hub
- **Single Entry** — fill in the 6 applicant fields, get an instant decision with an approval-probability dial, a benchmark comparison chart, and a risk diagnostic checklist.
- **Bulk Upload (CSV/Excel)** — evaluate hundreds of applicants at once, with a live progress bar, per-row validation errors, and a downloadable results table.

### Visual Analytics Dashboard
Automatically populated after a bulk upload:
- 5 KPI cards — total applications, approval rate, average credit score, average DTI, average loan amount.
- Scatter plot — DTI vs. Credit Score, color-coded by decision (green = Approved, red = Rejected).
- Bar chart — approval rate grouped by years-employed bracket.
- Histogram — loan amount distribution split by approved vs. denied.

### Report Export
Bulk evaluation results can be exported directly to a formatted **Excel workbook** or a **PowerPoint deck** (`report_generator.py`), complete with branded charts and summary tables — useful for handing results to a non-technical stakeholder.

### Developer / SDK Page
Live model telemetry pulled from the REST API, a downloadable `.pkl` model binary, and copy-paste integration snippets (Python, cURL, JavaScript).

---

## ⚙️ REST API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the single-page app |
| `GET` | `/api/health` | Health check — server status and whether the model loaded |
| `GET` | `/api/metadata` | Model metadata (algorithm, ROC-AUC, file size, status) |
| `GET` | `/api/model-info` | Kernel hyperparameters, support-vector counts, intercept |
| `GET` | `/api/features` | Feature schema with types, ranges, and descriptions |
| `POST` | `/api/predict` | Single applicant inference |
| `POST` | `/api/predict-bulk` | Bulk CSV/Excel inference |
| `GET` | `/api/download-template` | Download a pre-formatted CSV template |
| `GET` | `/api/download-model` | Download the trained `.pkl` model artifact |
| `POST` | `/api/export-excel` | Export bulk results as a formatted `.xlsx` report |
| `POST` | `/api/export-ppt` | Export bulk results as a `.pptx` deck |

### `POST /api/predict` — Request Body
```json
{
  "annual_income": 75000,
  "loan_amount": 15000,
  "credit_score": 720,
  "debt_to_income_ratio": 0.25,
  "years_employed": 5.0,
  "delinquencies_last_2yrs": 0
}
```

### `POST /api/predict` — Response
```json
{
  "success": true,
  "prediction": "Approved",
  "is_approved": true,
  "approval_probability": 0.956,
  "rejection_probability": 0.044,
  "approval_percentage": "95.6%",
  "decision_margin": 1.818,
  "risk_tier": "Prime / Low Risk",
  "benchmarks": { "...": "credit score / DTI / loan-to-income / delinquency comparisons" }
}
```

`debt_to_income_ratio` accepts either a decimal ratio (`0.25`) or a percentage (`25`) — the API normalizes it automatically. All inputs are strictly validated server-side (type, range, and required-field checks) before reaching the model.

---

## 🗂️ Project Structure

```
CrediVex-loan_Ai/
├── app.py                        # Flask application, validation, and all API routes
├── report_generator.py           # Excel & PowerPoint report generation (openpyxl/xlsxwriter, python-pptx)
├── loan_svc_project_2.pkl        # Trained pipeline (StandardScaler + SVC), served in production
├── Loan_approval_data_2025.csv   # Training dataset (50,000 records, 20 columns)
├── Project_Loan_final.ipynb      # Full training notebook: cleaning, hyperparameter search, evaluation
├── generate_data.py              # Generates a synthetic sample CSV for testing bulk upload
├── render.yaml                   # Render.com deployment config (gunicorn)
├── requirements.txt              # Python dependencies
│
├── templates/
│   └── index.html                # Single-page application shell
│
├── static/
│   ├── css/
│   │   ├── style.css             # Main CrediVex design system
│   │   └── visual_analytics.css  # Visual Analytics page styles
│   ├── js/
│   │   └── main.js               # SPA navigation, charts, bulk upload, analytics
│   ├── logos/
│   │   └── credivex_logo.jpg
│   └── favicon.ico
│
└── add_*.py, fix_app.py, refactor_validation*.py,
    update_*.py, process_logo.py  # One-off dev/maintenance scripts used while
                                   # iteratively building out features (bulk
                                   # endpoints, progress UI, theming, validation
                                   # refactors). Not required at runtime.
```

---

## 🎨 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10, Flask 3.x, Flask-CORS, Gunicorn |
| ML Pipeline | scikit-learn 1.9 (`StandardScaler` + `SVC`), joblib |
| Data handling | Pandas, NumPy, OpenPyXL |
| Reporting | XlsxWriter, python-pptx |
| Frontend | Vanilla JS (SPA), Chart.js 4.x |
| Styling | Custom CSS design system (Inter + Outfit fonts), Font Awesome 6 |

---

## 🛠️ Local Setup

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/eyar1230-hub/CrediVex-loan_Ai.git
cd CrediVex-loan_Ai

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python app.py
```

Open **http://localhost:5000** in your browser.

---

## ☁️ Deployment

The repo ships with a `render.yaml`, ready for one-click deployment to [Render](https://render.com):

```yaml
services:
  - type: web
    name: credivex-loan-app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

Set the `CORS_ORIGINS` environment variable to restrict allowed origins in production (defaults to `*`).

---

## 📦 Bulk Upload Format

Upload a `.csv` or `.xlsx` file with these exact column headers:

| Column | Type | Range |
|--------|------|-------|
| `annual_income` | float | ≥ 5,000 |
| `loan_amount` | float | ≥ 500 |
| `credit_score` | int | 300 – 850 |
| `debt_to_income_ratio` | float | 0.0 – 1.0 (or 0–100 as a percentage) |
| `years_employed` | float | 0 – 50 |
| `delinquencies_last_2yrs` | int | 0 – 30 |

> Download the pre-formatted template from the app: **Evaluation Hub → Bulk Upload → Download Template**, or generate a larger synthetic sample file with `python generate_data.py`.

---

## 📄 License

MIT License — feel free to fork and adapt.

---

*Built with ❤️ by [eyar1230](https://github.com/eyar1230-hub)*
