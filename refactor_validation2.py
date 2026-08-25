import os
import re

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to replace in api_predict
pattern = re.compile(r'# --- STRICT BACKEND VALIDATION ---.*?(?=if validation_errors:)', re.DOTALL)
replacement = '''# --- STRICT BACKEND VALIDATION ---
        validated_inputs, validation_errors = validate_and_extract_features(data)

        '''

new_content = pattern.sub(replacement, content, count=1)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
