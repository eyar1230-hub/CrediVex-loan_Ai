# 🏦 CREDIVEX — AI Loan Underwriting Engine

> **An interactive, full-stack loan approval platform powered by a Support Vector Classifier (SVC) with RBF kernel, built with Flask + Vanilla JS.**

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-SVC-orange?style=flat-square&logo=scikit-learn)
![Chart.js](https://img.shields.io/badge/Chart.js-4.x-pink?style=flat-square&logo=chart.js)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📸 Screenshots

| Overview | Evaluation Hub | Visual Analytics |
|----------|---------------|-----------------|
| Platform intro & model stats | Single & bulk loan evaluation | Portfolio charts & KPI dashboard |

---

## 🚀 Features

### 🤖 ML Model
- **Algorithm:** Support Vector Classifier (SVC) with RBF kernel
- **Accuracy:** 89.8% ROC-AUC on held-out test set
- **Pipeline:** `StandardScaler` → `SVC(kernel='rbf', C=7.308, γ=0.8, probability=True)` → Platt Scaling
- **Support Vectors:** 15,003 (Class 0: 7,440 | Class 1: 7,563)
- Evaluates **6 financial dimensions** per applicant

### 📋 Evaluation Hub
- **Single Entry** — fill in 6 fields, get instant prediction with:
  - Approval probability dial (doughnut chart)
  - Benchmark comparison bar chart
  - Risk diagnostic checklist
- **Bulk Upload (CSV/Excel)** — evaluate hundreds of applicants at once with a live progress bar and downloadable results table

### 📊 Visual Analytics Dashboard *(new)*
- Automatically populated after a bulk upload
- **5 KPI cards** — total applications, approval rate, avg credit score, avg DTI, avg loan amount
- **Scatter Plot** — Debt-to-Income Ratio vs Credit Score (FICO), colour-coded by model decision (green = Approved, red = Denied)
- **Bar Chart** — Approval rate % grouped by years-employed bracket (0–2, 3–5, 6–10, 11–20, 21+ years)
- **Histogram** — Loan amount distribution split by approved vs denied across monetary bands

### 🛠️ Developer & SDK Page
- Live model telemetry pulled from REST API
- Downloadable `.pkl` model binary
- Copy-paste code snippets (Python, cURL, JavaScript)

---

## 🗂️ Project Structure

```
CREDIVEX-loan-app/
├── app.py                      # Flask application & API routes
├── loan_svc_project_2.pkl      # Trained SVC pipeline (StandardScaler + SVC)
├── Loan_approval_data_2025.csv # Training dataset
│
├── templates/
│   └── index.html              # Single-page application (SPA)
│
├── static/
│   ├── css/
│   │   ├── style.css           # Main CREDIVEX design system
│   │   └── visual_analytics.css# Visual Analytics page styles
│   ├── js/
│   │   └── main.js             # SPA navigation, charts, bulk upload, analytics
│   ├── logos/
│   │   └── CREDIVEX_logo.jpg
│   └── favicon.ico
│
└── requirements.txt            # Python dependencies
```

---

## ⚙️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the SPA |
| `GET` | `/api/metadata` | Model metadata (accuracy, file size) |
| `GET` | `/api/model-info` | Kernel params, support vectors, intercept |
| `GET` | `/api/features` | Feature schema with ranges & descriptions |
| `POST` | `/api/predict` | Single applicant inference |
| `POST` | `/api/predict-bulk` | Bulk CSV/Excel inference |
| `GET` | `/api/download-template` | Download CSV template |
| `GET` | `/api/download-model` | Download `.pkl` model |

### `/api/predict` — Request Body

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

### `/api/predict` — Response

```json
{
  "success": true,
  "prediction": "Approved",
  "is_approved": true,
  "approval_probability": 0.956,
  "rejection_probability": 0.044,
  "approval_percentage": "95.6%",
  "decision_margin": 1.818,
  "risk_tier": "Prime / Low Risk"
}
```

---

## 🛠️ Local Setup

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/eyar1230-hub/CREDIVEX-loan-app.git
cd CREDIVEX-loan-app

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install flask scikit-learn pandas numpy openpyxl joblib

# 4. Run the server
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 📦 Bulk CSV Format

Upload a `.csv` or `.xlsx` file with these exact column headers:

| Column | Type | Range |
|--------|------|-------|
| `annual_income` | float | ≥ 5,000 |
| `loan_amount` | float | ≥ 500 |
| `credit_score` | int | 300 – 850 |
| `debt_to_income_ratio` | float | 0.0 – 1.0 |
| `years_employed` | float | 0 – 50 |
| `delinquencies_last_2yrs` | int | 0 – 30 |

> Download the pre-formatted template from the app: **Evaluation Hub → Bulk Upload → Download Template**

---

## 🎨 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10, Flask 3.x |
| ML Pipeline | Scikit-Learn (SVC + StandardScaler) |
| Frontend | Vanilla JS (SPA), Chart.js 4.x |
| Styling | Custom CSS design system (Inter + Outfit fonts) |
| Icons | Font Awesome 6 |
| Data | Pandas, NumPy, OpenPyXL |

---

## 📄 License

MIT License — feel free to fork and adapt.

---

*Built with ❤️ by [eyar1230](https://github.com/eyar1230-hub)*


