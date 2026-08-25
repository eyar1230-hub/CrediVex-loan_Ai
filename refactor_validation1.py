import os
import re

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# I will write a script to insert the shared validation function before /api/predict
validation_func = '''
def validate_and_extract_features(data):
    \"\"\"Validates raw input data and returns (validated_inputs, error_messages).\"\"\"
    validated_inputs = {}
    validation_errors = []

    # 1. annual_income
    try:
        val = float(data.get('annual_income', 0))
        if val <= 0:
            validation_errors.append("Annual income must be a positive number greater than 0.")
        elif val > 10000000:
            validation_errors.append("Annual income exceeds maximum supported limit (,000,000).")
        validated_inputs['annual_income'] = val
    except (ValueError, TypeError):
        validation_errors.append("Annual income must be a valid numeric value.")

    # 2. loan_amount
    try:
        val = float(data.get('loan_amount', 0))
        if val <= 0:
            validation_errors.append("Loan amount must be a positive number greater than 0.")
        elif val > 2000000:
            validation_errors.append("Loan amount exceeds maximum loan cap (,000,000).")
        validated_inputs['loan_amount'] = val
    except (ValueError, TypeError):
        validation_errors.append("Loan amount must be a valid numeric value.")

    # 3. credit_score
    try:
        val = int(round(float(data.get('credit_score', 0))))
        if val < 300 or val > 850:
            validation_errors.append("Credit score must be between 300 and 850 (FICO standard).")
        validated_inputs['credit_score'] = val
    except (ValueError, TypeError):
        validation_errors.append("Credit score must be an integer between 300 and 850.")

    # 4. debt_to_income_ratio (Accept both decimals like 0.35 and percentages like 35)
    try:
        raw_dti = float(data.get('debt_to_income_ratio', -1))
        if raw_dti > 1.0 and raw_dti <= 100.0:
            raw_dti = raw_dti / 100.0  # Normalize percentage to ratio
        if raw_dti < 0.0 or raw_dti > 1.0:
            validation_errors.append("Debt-to-income ratio must be between 0.0 and 1.0 (0% to 100%).")
        validated_inputs['debt_to_income_ratio'] = raw_dti
    except (ValueError, TypeError):
        validation_errors.append("Debt-to-income ratio must be a valid numeric ratio between 0.0 and 1.0.")

    # 5. years_employed
    try:
        val = float(data.get('years_employed', -1))
        if val < 0.0 or val > 60.0:
            validation_errors.append("Years employed must be between 0 and 60 years.")
        validated_inputs['years_employed'] = val
    except (ValueError, TypeError):
        validation_errors.append("Years employed must be a positive number.")

    # 6. delinquencies_last_2yrs
    try:
        val = int(round(float(data.get('delinquencies_last_2yrs', -1))))
        if val < 0 or val > 30:
            validation_errors.append("Delinquencies count must be an integer between 0 and 30.")
        validated_inputs['delinquencies_last_2yrs'] = val
    except (ValueError, TypeError):
        validation_errors.append("Delinquencies must be an integer.")

    return validated_inputs, validation_errors
'''

# Find the start of api_predict
predict_idx = content.find('@app.route(\'/api/predict\', methods=[\'POST\'])')

new_content = content[:predict_idx] + validation_func + '\n\n' + content[predict_idx:]

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
