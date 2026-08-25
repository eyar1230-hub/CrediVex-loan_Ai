import os
import re

css_path = 'static/css/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_palette = '''    /* Core Palette - Vibrant Multi-Color */
    --color-green: #059669; 
    --color-turquoise: #0891b2;
    --color-sapphire: #0F52BA;
    --color-amethyst: #9333ea;
    --color-coral: #f43f5e;
    --color-gold: #eab308;

    --color-red: #dc2626;

    /* Neutrals & Vibrant Background */
    --bg-body: linear-gradient(135deg, #e6f7ec 0%, #e0f7fa 25%, #e6eeff 50%, #f3e8ff 75%, #ffe4e6 100%);
    --bg-card: rgba(255, 255, 255, 0.85); /* Slightly transparent cards to show the colorful bg */
    --border-color: #e2e8f0;
    --border-color-hover: #cbd5e1;

    /* Text Colors */
    --text-heading: #0a3161; 
    --text-body: #1e293b;
    --text-muted: #475569;
    --text-light: #64748b;'''

# Replace palette
pattern = re.compile(r'    /\* Core Palette.*?(?=    /\* Typography \*/)', re.DOTALL)
content = pattern.sub(new_palette + '\n\n', content)

# Let's also inject some CSS for gradient text on headings
gradient_css = '''
h1, h2 {
    background: linear-gradient(to right, var(--color-sapphire), var(--color-amethyst), var(--color-coral));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    color: transparent;
    display: inline-block;
}

.card {
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}
'''

content = content + '\n' + gradient_css

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(content)
