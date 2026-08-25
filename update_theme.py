import os

css_path = 'static/css/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace body background-color to background
content = content.replace('background-color: var(--bg-body);', 'background: var(--bg-body);')

new_palette = '''    /* Core Palette - Mountain Theme */
    --color-green: #2563eb; /* Icy Blue */
    --color-green-light: #eff6ff;
    --color-green-border: #bfdbfe;

    --color-turquoise: #334155; /* Deep Slate Base */
    --color-turquoise-light: #f8fafc;
    --color-turquoise-border: #e2e8f0;

    --color-orange: #d97706; /* Golden Sunrise Highlight */
    --color-orange-light: #fffbeb;

    --color-red: #dc2626;
    --color-red-light: #fef2f2;
    --color-red-border: #fecaca;

    /* Neutrals */
    --bg-body: linear-gradient(180deg, #d3dee8 0%, #f5f4ef 100%);'''

import re
pattern = re.compile(r'/\* Core Palette \*/.*?--bg-body: #[a-f0-9]+;', re.DOTALL)
content = pattern.sub(new_palette, content)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(content)
