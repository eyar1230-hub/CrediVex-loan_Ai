import os
import re

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

bulk_endpoints = '''
import io
import csv

@app.route('/api/download-template', methods=['GET'])
def api_download_template():
    \"\"\"Generates a CSV template for bulk evaluation.\"\"\"
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
        download_name='lendwell_bulk_template.csv'
    )

@app.route('/api/predict-bulk', methods=['POST'])
def api_predict_bulk():
    \"\"\"Processes a bulk CSV or Excel upload.\"\"\"
    if 'file' not in request.files:
        return jsonify({\"success\": False, \"error\": \"No file uploaded.\"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({\"success\": False, \"error\": \"Empty filename.\"}), 400
        
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xls') or file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return jsonify({\"success\": False, \"error\": \"Unsupported file format. Please upload a .csv or .xlsx file.\"}), 400
    except Exception as e:
        return jsonify({\"success\": False, \"error\": f\"Error reading file: {str(e)}\"}), 400
        
    # Check if required columns are present
    missing_cols = [col for col in FEATURE_NAMES if col not in df.columns]
    if missing_cols:
        return jsonify({\"success\": False, \"error\": f\"Missing required columns: {', '.join(missing_cols)}\"}), 400
        
    results = []
    errors = []
    
    for index, row in df.iterrows():
        # Convert row to dictionary
        data = row.to_dict()
        row_num = index + 2 # +1 for 0-index, +1 for header
        
        validated_inputs, validation_errors = validate_and_extract_features(data)
        
        if validation_errors:
            errors.append({
                \"row\": row_num,
                \"messages\": validation_errors
            })
            continue
            
        if pipeline is None:
            errors.append({\"row\": row_num, \"messages\": [\"ML Pipeline is not currently loaded.\"]})
            continue
            
        # Inference
        input_df = pd.DataFrame([[
            validated_inputs['annual_income'],
            validated_inputs['loan_amount'],
            validated_inputs['credit_score'],
            validated_inputs['debt_to_income_ratio'],
            validated_inputs['years_employed'],
            validated_inputs['delinquencies_last_2yrs']
        ]], columns=FEATURE_NAMES)
        
        raw_pred = pipeline.predict(input_df)[0]
        prediction_class = int(round(float(raw_pred)))
        is_approved = (prediction_class == 1)
        prediction_label = "Approved" if is_approved else "Rejected"
        
        # Probabilities
        if hasattr(pipeline, 'predict_proba'):
            probas = pipeline.predict_proba(input_df)[0]
            p_reject, p_approve = float(probas[0]), float(probas[1])
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
            \"row\": row_num,
            \"prediction\": prediction_label,
            \"is_approved\": is_approved,
            \"approval_percentage\": f\"{p_approve * 100:.1f}%\",
            \"risk_tier\": risk_tier,
            \"inputs\": validated_inputs
        })
        
    return jsonify({
        \"success\": True,
        \"results\": results,
        \"errors\": errors,
        \"total_rows\": len(df),
        \"valid_count\": len(results),
        \"error_count\": len(errors)
    })
'''

# Find the end of the file to append
new_content = content + '\n' + bulk_endpoints + '\n'

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
