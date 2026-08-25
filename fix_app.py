import os
import re

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Separate the main block and the appended bulk code
main_block = '''# 3. Server Entry Point
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Starting Loan Approval SVC Server on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)'''

# find the main block
main_idx = content.find(main_block)

before = content[:main_idx]
after = content[main_idx + len(main_block):] # this has the appended endpoints

# Fix imports since I added import io and import csv
imports = "import io\nimport csv\n"

# Rewrite the file
new_content = imports + before + after + '\n\n' + main_block

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
