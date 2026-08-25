import os

html_path = r'C:\Users\eyar1\ECOM\antigravity works\Project_Loan\templates\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Title
content = content.replace('<title>AuraLoan — AI Credit Underwriting Engine</title>', 
                          '<link rel=\"icon\" type=\"image/x-icon\" href=\"/static/favicon.ico\">\n    <title>Lendwell — AI Credit Underwriting Engine</title>')

# Replace Brand Logo and Name
old_brand = '<div class=\"brand-badge\">?</div>\n                <div class=\"brand-name\">Aura<span>Loan</span></div>'
new_brand = '<img src=\"/static/logos/lendwell_logo.jpg\" alt=\"Lendwell Logo\" class=\"brand-logo\" style=\"height: 40px; border-radius: 6px; margin-right: 8px;\">\n                <div class=\"brand-name\">Lendwell</div>'
content = content.replace(old_brand, new_brand)

# Replace AuraLoan text
content = content.replace('Welcome to AuraLoan.', 'Welcome to Lendwell.')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated index.html')
