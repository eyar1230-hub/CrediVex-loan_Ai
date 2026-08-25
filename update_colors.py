import os
import re

css_path = 'static/css/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_palette = '''    /* Core Palette - Green, Turquoise, Sapphire */
    --color-green: #059669; /* Rich Green */
    --color-green-light: #ecfdf5;
    --color-green-border: #a7f3d0;

    --color-turquoise: #0891b2; /* Bright Turquoise */
    --color-turquoise-light: #cffafe;
    --color-turquoise-border: #a5f3fc;

    --color-orange: #0F52BA; /* Sapphire Blue (Replaced orange for button highlights) */
    --color-orange-light: #eff6ff;

    --color-red: #dc2626;
    --color-red-light: #fef2f2;
    --color-red-border: #fecaca;

    /* Neutrals & Background */
    --bg-body: linear-gradient(135deg, #e6f7ec 0%, #e0f7fa 50%, #e6eeff 100%);
    --bg-card: #ffffff;
    --border-color: #e2e8f0;
    --border-color-hover: #cbd5e1;

    /* Text Colors */
    --text-heading: #0a3161; /* Deep Sapphire Blue */
    --text-body: #164e63; /* Deep Turquoise Dark */
    --text-muted: #334155;
    --text-light: #64748b;'''

pattern = re.compile(r'    /\* Core Palette.*?(?=    /\* Typography \*/)', re.DOTALL)
content = pattern.sub(new_palette + '\n\n', content)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(content)
