import io
import csv
import os
import traceback
import joblib
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request, render_template, send_file, send_from_directory
from flask_cors import CORS
from report_generator import generate_excel_report, generate_ppt_report

# 1. Initialize Flask Application
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
CORS(app, origins=os.environ.get("CORS_ORIGINS", "*").split(","))

# 2. Configuration & Model Initialization
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILENAME = 'loan_svc_project_2.pkl'
MODEL_PATH = os.path.join(BASE_DIR, MODEL_FILENAME)

# Hardcoded reference stats from the trained winning model
ROC_AUC_SCORE = 0.8977
MODEL_STATUS = "Production Ready"

# Ordered list of features expected by the scikit-learn pipeline
FEATURE_NAMES = [
    'annual_income',
    'loan_amount',
    'credit_score',
    'debt_to_income_ratio',
    'years_employed',
    'delinquencies_last_2yrs'
]

FEATURE_METADATA = {
    'annual_income': {
        'label': 'Annual Income',
        'type': 'float',
        'unit': '$',
        'min': 5000,
        'max': 1000000,
        'description': 'Gross annual income before taxes and deductions'
    },
    'loan_amount': {
        'label': 'Loan Amount',
        'type': 'float',
        'unit': '$',
        'min': 500,
        'max': 500000,
        'description': 'Total principal amount requested for the loan'
    },
    'credit_score': {
        'label': 'Credit Score (FICO)',
        'type': 'integer',
        'unit': 'pts',
        'min': 300,
        'max': 850,
        'description': 'Standard credit bureau risk score (300 - 850)'
    },
    'debt_to_income_ratio': {
        'label': 'Debt-to-Income (DTI)',
        'type': 'float',
        'unit': 'ratio',
        'min': 0.0,
        'max': 1.0,
        'description': 'Total monthly debt payments divided by gross monthly income (e.g. 0.28 for 28%)'
    },
    'years_employed': {
        'label': 'Years Employed',
        'type': 'float',
        'unit': 'years',
        'min': 0.0,
        'max': 50.0,
        'description': 'Continuous years of verified employment history'
    },
    'delinquencies_last_2yrs': {
        'label': 'Delinquencies (Last 2 Yrs)',
        'type': 'integer',
        'unit': 'count',
        'min': 0,
        'max': 30,
        'description': 'Number of 30+ days past due payment delinquencies in the past 24 months'
    }
}

# Attempt to load the pre-trained pipeline
pipeline = None
try:
    if os.path.exists(MODEL_PATH):
        pipeline = joblib.load(MODEL_PATH)
        print(f"[SUCCESS] Loaded model pipeline from: {MODEL_PATH}")
    else:
        # Fallback to alternate name if present
        alt_path = os.path.join(BASE_DIR, 'loan_svc_project.pkl')
        if os.path.exists(alt_path):
            pipeline = joblib.load(alt_path)
            MODEL_PATH = alt_path
            MODEL_FILENAME = 'loan_svc_project.pkl'
            print(f"[INFO] Loaded alternate model pipeline from: {alt_path}")
        else:
            print(f"[WARNING] Model file {MODEL_FILENAME} not found at {MODEL_PATH}")
except Exception as e:
    print(f"[ERROR] Failed to load model file: {e}")
    traceback.print_exc()


# --- HELPER FUNCTIONS ---

def extract_model_info():
    """Extract structural parameters and RBF kernel margin info from the pipeline."""
    if pipeline is None:
        return {
            "status": "Model Not Loaded",
            "kernel_type": "rbf",
            "calculation_function": "f(x) = sign( sum(alpha_i * y_i * exp(-gamma * ||x_i - x||^2)) + b )",
            "intercept_b": -0.3442,
            "total_support_vectors": 15003,
            "gamma": 0.8,
            "C_regularization": 7.308,
            "class_weight": "{0: 1.0, 1: 1.0}",
            "scaling_step": "StandardScaler(with_mean=True, with_std=True)",
            "classes": ["0: Rejected", "1: Approved"]
        }

    try:
        svc_engine = pipeline.named_steps.get('svc')
        scaler_step = pipeline.named_steps.get('scaler')

        intercept_val = float(svc_engine.intercept_[0]) if hasattr(svc_engine, 'intercept_') else -0.3442
        n_sv = sum(svc_engine.n_support_) if hasattr(svc_engine, 'n_support_') else 15003
        n_sv_per_class = [int(x) for x in svc_engine.n_support_] if hasattr(svc_engine, 'n_support_') else [7440, 7563]
        gamma_val = float(svc_engine.gamma) if isinstance(svc_engine.gamma, (int, float)) else str(svc_engine.gamma)
        c_val = float(svc_engine.C) if hasattr(svc_engine, 'C') else 7.308

        return {
            "kernel_type": str(svc_engine.kernel),
            "calculation_function": "f(x) = sign( sum(alpha_i * y_i * exp(-gamma * ||x_i - x||^2)) + b )",
            "decision_function_formula": "decision_margin = sum(alpha_i * y_i * K(x_i, x)) + b",
            "rbf_kernel_formula": "K(x_i, x) = exp( -gamma * ||x_i - x||^2 )",
            "intercept_b": round(intercept_val, 6),
            "total_support_vectors": n_sv,
            "support_vectors_per_class": {
                "class_0_rejected": n_sv_per_class[0],
                "class_1_approved": n_sv_per_class[1]
            },
            "gamma": gamma_val,
            "C_regularization": c_val,
            "class_weight": str(svc_engine.class_weight),
            "probability_calibration_enabled": bool(svc_engine.probability),
            "scaler_type": str(scaler_step.__class__.__name__),
            "pipeline_steps": [str(name) for name in pipeline.named_steps.keys()],
            "classes": [int(c) for c in pipeline.classes_] if hasattr(pipeline, 'classes_') else [0, 1]
        }
    except Exception as e:
        return {
            "kernel_type": "rbf",
            "calculation_function": "f(x) = sign( sum(alpha_i * y_i * exp(-gamma * ||x_i - x||^2)) + b )",
            "intercept_b": -0.344238,
            "total_support_vectors": 15003,
            "gamma": 0.8,
            "C_regularization": 7.308,
            "error": str(e)
        }


# --- REST API ENDPOINTS ---

@app.route('/')
def index():
    """Serves the main single-page UI for the Loan Approval application."""
    return render_template('index.html')


@app.route('/api/features', methods=['GET'])
def api_features():
    """
    Returns the required list of 6 input features with rich descriptive metadata.
    """
    return jsonify({
        "features": FEATURE_NAMES,
        "feature_count": len(FEATURE_NAMES),
        "metadata": FEATURE_METADATA
    })


@app.route('/api/model-info', methods=['GET'])
def api_model_info():
    """
    Returns the RBF model's margin data, mathematical calculation function,
    support vector distribution, and kernel hyperparameters.
    """
    info = extract_model_info()
    return jsonify(info)


@app.route('/api/metadata', methods=['GET'])
def api_metadata():
    """
    Returns model metadata including filename, winning ROC AUC score,
    model version, and operational status.
    """
    file_size_bytes = os.path.getsize(MODEL_PATH) if os.path.exists(MODEL_PATH) else 0
    return jsonify({
        "file_name": MODEL_FILENAME,
        "model_accuracy_roc_auc": ROC_AUC_SCORE,
        "roc_auc_percentage": f"{ROC_AUC_SCORE * 100:.2f}%",
        "algorithm": "Support Vector Classifier (SVC) with RBF Kernel",
        "preprocessing": "StandardScaler (Z-Score Normalization)",
        "file_size_kb": round(file_size_bytes / 1024, 2),
        "status": MODEL_STATUS,
        "framework": "scikit-learn",
        "features_expected": len(FEATURE_NAMES)
    })



def validate_and_extract_features(data):
    """Validates raw input data and returns (validated_inputs, error_messages)."""
    validated_inputs = {}
    validation_errors = []

    # 1. annual_income
    if 'annual_income' not in data or data['annual_income'] is None or data['annual_income'] == '':
        validation_errors.append("'annual_income' is a required field.")
    else:
        try:
            val = float(data['annual_income'])
            if val <= 0:
                validation_errors.append("Annual income must be a positive number greater than 0.")
            elif val > 10000000:
                validation_errors.append("Annual income exceeds maximum supported limit ($10,000,000).")
            else:
                validated_inputs['annual_income'] = val
        except (ValueError, TypeError):
            validation_errors.append("Annual income must be a valid numeric value.")

    # 2. loan_amount
    if 'loan_amount' not in data or data['loan_amount'] is None or data['loan_amount'] == '':
        validation_errors.append("'loan_amount' is a required field.")
    else:
        try:
            val = float(data['loan_amount'])
            if val <= 0:
                validation_errors.append("Loan amount must be a positive number greater than 0.")
            elif val > 2000000:
                validation_errors.append("Loan amount exceeds maximum loan cap ($2,000,000).")
            else:
                validated_inputs['loan_amount'] = val
        except (ValueError, TypeError):
            validation_errors.append("Loan amount must be a valid numeric value.")

    # 3. credit_score
    if 'credit_score' not in data or data['credit_score'] is None or data['credit_score'] == '':
        validation_errors.append("'credit_score' is a required field.")
    else:
        try:
            val = round(float(data['credit_score']))
            if val < 300 or val > 850:
                validation_errors.append("Credit score must be between 300 and 850 (FICO standard).")
            else:
                validated_inputs['credit_score'] = val
        except (ValueError, TypeError):
            validation_errors.append("Credit score must be an integer between 300 and 850.")

    # 4. debt_to_income_ratio (Accept both decimals like 0.35 and percentages like 35)
    if 'debt_to_income_ratio' not in data or data['debt_to_income_ratio'] is None or data['debt_to_income_ratio'] == '':
        validation_errors.append("'debt_to_income_ratio' is a required field.")
    else:
        try:
            raw_dti = float(data['debt_to_income_ratio'])
            if raw_dti < 0.0:
                validation_errors.append("Debt-to-income ratio cannot be negative.")
            elif raw_dti > 100.0:
                validation_errors.append("Debt-to-income ratio must be between 0.0 and 1.0 (as a ratio) or 0 to 100 (as a percentage).")
            else:
                if raw_dti > 1.0:
                    raw_dti = raw_dti / 100.0  # Normalize percentage to ratio
                validated_inputs['debt_to_income_ratio'] = raw_dti
        except (ValueError, TypeError):
            validation_errors.append("Debt-to-income ratio must be a valid numeric value.")

    # 5. years_employed
    if 'years_employed' not in data or data['years_employed'] is None or data['years_employed'] == '':
        validation_errors.append("'years_employed' is a required field.")
    else:
        try:
            val = float(data['years_employed'])
            if val < 0.0 or val > 60.0:
                validation_errors.append("Years employed must be between 0 and 60 years.")
            else:
                validated_inputs['years_employed'] = val
        except (ValueError, TypeError):
            validation_errors.append("Years employed must be a positive number.")

    # 6. delinquencies_last_2yrs
    if 'delinquencies_last_2yrs' not in data or data['delinquencies_last_2yrs'] is None or data['delinquencies_last_2yrs'] == '':
        validation_errors.append("'delinquencies_last_2yrs' is a required field.")
    else:
        try:
            val = round(float(data['delinquencies_last_2yrs']))
            if val < 0 or val > 30:
                validation_errors.append("Delinquencies count must be an integer between 0 and 30.")
            else:
                validated_inputs['delinquencies_last_2yrs'] = val
        except (ValueError, TypeError):
            validation_errors.append("Delinquencies must be an integer.")

    return validated_inputs, validation_errors


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    Accepts JSON payload containing the 6 financial features:
    - annual_income (float > 0)
    - loan_amount (float > 0)
    - credit_score (int: 300 to 850)
    - debt_to_income_ratio (float: 0.0 to 1.0)
    - years_employed (float >= 0)
    - delinquencies_last_2yrs (int >= 0)

    Returns:
    - prediction: 'Approved' or 'Rejected'
    - class_label: 1 or 0
    - approval_probability: float (0.0 - 1.0)
    - rejection_probability: float (0.0 - 1.0)
    - decision_margin: distance to RBF separating hyperplane
    - risk_tier: 'Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk'
    - timestamp & sanitized inputs
    """
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid request body. Expected application/json with feature values."
            }), 400

        # --- STRICT BACKEND VALIDATION ---
        validated_inputs, validation_errors = validate_and_extract_features(data)

        if validation_errors:
            return jsonify({
                "success": False,
                "error": "Validation failed",
                "validation_errors": validation_errors
            }), 422

        # Create input DataFrame strictly matching training features
        input_df = pd.DataFrame([[
            validated_inputs['annual_income'],
            validated_inputs['loan_amount'],
            validated_inputs['credit_score'],
            validated_inputs['debt_to_income_ratio'],
            validated_inputs['years_employed'],
            validated_inputs['delinquencies_last_2yrs']
        ]], columns=FEATURE_NAMES)

        if pipeline is None:
            # Fallback heuristic calculation if model file was not loaded
            return jsonify({
                "success": False,
                "error": "ML Pipeline is not currently loaded on the server."
            }), 503

        # Model Inference
        raw_pred = pipeline.predict(input_df)[0]
        prediction_class = round(float(raw_pred))
        is_approved = (prediction_class == 1)
        prediction_label = "Approved" if is_approved else "Rejected"

        # Probability Estimation
        try:
            probas = pipeline.predict_proba(input_df)[0]
            # Match classes: [0, 1]
            p_reject = float(probas[0])
            p_approve = float(probas[1])
        except Exception:
            p_approve = 0.90 if is_approved else 0.10
            p_reject = 1.0 - p_approve

        # Decision Function Margin
        decision_margin = 0.0
        if hasattr(pipeline, 'decision_function'):
            decision_margin = float(pipeline.decision_function(input_df)[0])

        # Risk Tier Classification
        if p_approve >= 0.80:
            risk_tier = "Prime / Low Risk"
            risk_color = "#00F5A0"
        elif p_approve >= 0.50:
            risk_tier = "Moderate / Near-Prime Risk"
            risk_color = "#3B82F6"
        elif p_approve >= 0.25:
            risk_tier = "High Risk / Subprime"
            risk_color = "#F59E0B"
        else:
            risk_tier = "Critical Risk / High Default Probability"
            risk_color = "#FF3366"

        # Benchmark comparison metrics for UI charts
        annual_inc = validated_inputs.get('annual_income', 0)
        loan_to_income = (validated_inputs['loan_amount'] / annual_inc) if annual_inc > 0 else float('inf')
        benchmarks = {
            "credit_score": {
                "value": validated_inputs['credit_score'],
                "safe_benchmark": 670,
                "status": "Healthy" if validated_inputs['credit_score'] >= 670 else "At Risk"
            },
            "debt_to_income": {
                "value": round(validated_inputs['debt_to_income_ratio'] * 100, 1),
                "safe_benchmark": 36.0,
                "status": "Healthy" if validated_inputs['debt_to_income_ratio'] <= 0.36 else "Elevated"
            },
            "loan_to_income_ratio": {
                "value": round(loan_to_income, 2),
                "safe_benchmark": 0.40,
                "status": "Healthy" if loan_to_income <= 0.40 else "High Leverage"
            },
            "delinquencies": {
                "value": validated_inputs['delinquencies_last_2yrs'],
                "safe_benchmark": 0,
                "status": "Clean" if validated_inputs['delinquencies_last_2yrs'] == 0 else "Adverse History"
            }
        }

        return jsonify({
            "success": True,
            "prediction": prediction_label,
            "is_approved": is_approved,
            "class_label": prediction_class,
            "approval_probability": round(p_approve, 4),
            "approval_percentage": f"{p_approve * 100:.1f}%",
            "rejection_probability": round(p_reject, 4),
            "rejection_percentage": f"{p_reject * 100:.1f}%",
            "decision_margin": round(decision_margin, 4),
            "risk_tier": risk_tier,
            "risk_color": risk_color,
            "benchmarks": benchmarks,
            "inputs": validated_inputs
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Internal inference error: {str(e)}"
        }), 500


@app.route('/api/download-model', methods=['GET'])
def api_download_model():
    """
    Allows downloading the trained .pkl scikit-learn model artifact.
    """
    if os.path.exists(MODEL_PATH):
        return send_file(
            MODEL_PATH,
            as_attachment=True,
            download_name=MODEL_FILENAME,
            mimetype='application/octet-stream'
        )
    return jsonify({"error": "Model file not found on server."}), 404


@app.route('/api/health', methods=['GET'])
def api_health():
    """System health check endpoint."""
    return jsonify({
        "status": "healthy",
        "model_loaded": pipeline is not None,
        "model_path": MODEL_PATH
    })

@app.route('/api/download-template', methods=['GET'])
def api_download_template():
    """Generates a CSV template for bulk evaluation."""
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(FEATURE_NAMES)
    
    # Write a sample valid row for guidance
    cw.writerow([75000, 15000, 720, 0.28, 5, 0])
    
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='credivex_bulk_template.csv'
    )

@app.route('/api/predict-bulk', methods=['POST'])
def api_predict_bulk():
    """Processes a bulk CSV or Excel upload."""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded."}), 400
        
    file = request.files['file']
    filename = file.filename
    if not isinstance(filename, str) or filename == '':
        return jsonify({"success": False, "error": "Empty filename."}), 400
        
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file.stream)
        elif filename.endswith('.xls') or filename.endswith('.xlsx'):
            df = pd.read_excel(file.stream)
        else:
            return jsonify({"success": False, "error": "Unsupported file format. Please upload a .csv or .xlsx file."}), 400
            
        # Clean up empty/incomplete rows that cause NaN errors in the ML pipeline
        # Drop rows where ALL values are missing (like trailing commas ',,,,,')
        df = df.dropna(how='all')
        
        # Fill remaining missing values with a dummy string to trigger the validation errors properly
        # instead of passing NaNs to the model
        df = df.fillna("")
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error reading file: {str(e)}"}), 400
        
    # Check if required columns are present
    missing_cols = [col for col in FEATURE_NAMES if col not in df.columns]
    if missing_cols:
        return jsonify({"success": False, "error": f"Missing required columns: {', '.join(missing_cols)}"}), 400
        
    results = []
    errors = []
    
    try:
        valid_indices = []
        valid_inputs_list = []

        for i, (_, row) in enumerate(df.iterrows()):
            # Convert row to dictionary
            data = row.to_dict()
            row_num = i + 2 # +1 for 0-index, +1 for header
            
            validated_inputs, validation_errors = validate_and_extract_features(data)
            
            if validation_errors:
                errors.append({
                    "row": row_num,
                    "messages": validation_errors
                })
                continue
                
            valid_indices.append(row_num)
            valid_inputs_list.append(validated_inputs)

        if pipeline is None:
            return jsonify({"success": False, "error": "ML Pipeline is not currently loaded."}), 500

        if len(valid_inputs_list) > 0:
            # Batch Inference (1000x faster than calling .predict() in a loop)
            input_df = pd.DataFrame(valid_inputs_list, columns=FEATURE_NAMES)
            
            raw_preds = pipeline.predict(input_df)
            probas = pipeline.predict_proba(input_df) if hasattr(pipeline, 'predict_proba') else None
            
            for idx in range(len(valid_inputs_list)):
                row_num = valid_indices[idx]
                val_inputs = valid_inputs_list[idx]
                
                raw_pred = raw_preds[idx]
                prediction_class = round(float(raw_pred))
                is_approved = (prediction_class == 1)
                prediction_label = "Approved" if is_approved else "Rejected"
                
                # Probabilities
                if probas is not None:
                    p_reject, p_approve = float(probas[idx][0]), float(probas[idx][1])
                else:
                    p_approve = 0.90 if is_approved else 0.10
                    p_reject = 1.0 - p_approve
                    
                # Risk Tier
                if p_approve >= 0.80:
                    risk_tier = "Prime / Low Risk"
                elif p_approve >= 0.50:
                    risk_tier = "Moderate Risk"
                elif p_approve >= 0.25:
                    risk_tier = "High Risk"
                else:
                    risk_tier = "Critical Risk"
                    
                results.append({
                    "row": row_num,
                    "prediction": prediction_label,
                    "is_approved": is_approved,
                    "approval_percentage": f"{p_approve * 100:.1f}%",
                    "risk_tier": risk_tier,
                    "inputs": val_inputs
                })
            
        return jsonify({
            "success": True,
            "results": results,
            "errors": errors,
            "total_rows": len(df),
            "valid_count": len(results),
            "error_count": len(errors)
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Inference error: {str(e)}"}), 500


@app.route('/api/export-excel', methods=['POST'])
def api_export_excel():
    data = request.get_json(force=True, silent=True)
    if not data or not isinstance(data, list):
        return jsonify({"success": False, "error": "Invalid data format."}), 400
    try:
        output = generate_excel_report(data)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='Credivex_Evaluation_Results.xlsx'
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/export-ppt', methods=['POST'])
def api_export_ppt():
    data = request.get_json(force=True, silent=True)
    if not data or not isinstance(data, list):
        return jsonify({"success": False, "error": "Invalid data format."}), 400
    try:
        output = generate_ppt_report(data)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation',
            as_attachment=True,
            download_name='Credivex_Evaluation_Results.pptx'
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 3. Server Entry Point
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    print(f"[*] Starting Loan Approval SVC Server on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)


