import os
import re

html_path = r'C:\Users\eyar1\ECOM\antigravity works\Project_Loan\templates\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_loading = '<div id="bulkLoading" style="display: none;"><i class="fa-solid fa-circle-notch fa-spin"></i> Processing...</div>'

new_loading = '''
                    <div id="bulkLoading" style="display: none; width: 100%; margin-top: 20px; text-align: left;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span style="font-weight: 600; color: var(--color-sapphire);"><i class="fa-solid fa-gears"></i> Processing Data...</span>
                            <span id="bulkProgressText" style="font-weight: bold; color: var(--color-sapphire);">0%</span>
                        </div>
                        <div style="width: 100%; background-color: #e2e8f0; border-radius: 999px; height: 12px; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);">
                            <div id="bulkProgressBar" style="height: 100%; width: 0%; background: linear-gradient(90deg, var(--color-sapphire), var(--color-turquoise)); border-radius: 999px; transition: width 0.4s ease;"></div>
                        </div>
                        <p id="bulkProgressDetail" style="font-size: 0.85em; color: var(--text-muted); margin-top: 8px;">Initializing...</p>
                    </div>
'''

content = content.replace(old_loading, new_loading)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)
