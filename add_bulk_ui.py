import os

html_path = r'C:\Users\eyar1\ECOM\antigravity works\Project_Loan\templates\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

toggle_html = '''
            <!-- Mode Toggle -->
            <div style="margin-bottom: 20px; display: flex; gap: 10px;">
                <button id="btnModeSingle" class="btn btn-primary" onclick="setEvalMode('single')">Single Entry</button>
                <button id="btnModeBulk" class="btn btn-outline" onclick="setEvalMode('bulk')">Bulk Upload (CSV)</button>
            </div>
'''

content = content.replace('<!-- Quick Preset Bar -->', toggle_html + '            <!-- Quick Preset Bar -->')

# Now add the Bulk Upload UI inside the eval-layout, initially hidden.
bulk_ui = '''
            <!-- BULK UPLOAD LAYOUT -->
            <div class="eval-layout" id="bulkLayout" style="display: none; flex-direction: column;">
                <div class="card form-card" style="width: 100%; max-width: none; text-align: center; padding: 40px;">
                    <h3>Bulk CSV/Excel Evaluation</h3>
                    <p style="margin-bottom: 20px;">Upload a spreadsheet to evaluate multiple loan applications at once.</p>
                    <div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 30px;">
                        <a href="/api/download-template" class="btn btn-secondary"><i class="fa-solid fa-download"></i> Download Template</a>
                        <label class="btn btn-primary" style="cursor: pointer;">
                            <i class="fa-solid fa-upload"></i> Upload CSV/Excel
                            <input type="file" id="bulkFileInput" accept=".csv, .xls, .xlsx" style="display: none;" onchange="handleBulkUpload(event)">
                        </label>
                    </div>
                    <div id="bulkLoading" style="display: none;"><i class="fa-solid fa-circle-notch fa-spin"></i> Processing...</div>
                </div>
                
                <div id="bulkErrorPanel" class="card" style="display: none; border-left: 4px solid #FF3366; background: #fff5f5; width: 100%; margin-top: 20px;">
                    <h4 style="color: #FF3366; margin-top: 0;"><i class="fa-solid fa-triangle-exclamation"></i> Validation Errors</h4>
                    <p style="font-size: 0.9em; margin-bottom: 10px;">The following rows had errors and were skipped. Please correct them and re-upload.</p>
                    <ul id="bulkErrorList" style="font-size: 0.85em; color: #555; text-align: left; padding-left: 20px;"></ul>
                </div>

                <div id="bulkResultsPanel" class="card" style="display: none; width: 100%; margin-top: 20px;">
                    <h3 style="margin-top: 0;">Evaluation Results (<span id="bulkValidCount">0</span> processed)</h3>
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; text-align: left; margin-top: 15px;">
                            <thead>
                                <tr style="border-bottom: 2px solid #eee;">
                                    <th style="padding: 10px;">Row</th>
                                    <th style="padding: 10px;">Income</th>
                                    <th style="padding: 10px;">Loan Amt</th>
                                    <th style="padding: 10px;">Verdict</th>
                                    <th style="padding: 10px;">Approval %</th>
                                    <th style="padding: 10px;">Risk Tier</th>
                                </tr>
                            </thead>
                            <tbody id="bulkResultsTableBody">
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
'''

# insert bulk_ui after the end of eval-layout
end_eval_layout = content.find('</section>', content.find('<!-- 2-Column Evaluator Layout -->'))
content = content[:end_eval_layout] + bulk_ui + '\n        ' + content[end_eval_layout:]

# Add id to the single layout to hide it
content = content.replace('<div class="eval-layout">', '<div class="eval-layout" id="singleLayout">')
content = content.replace('<div class="preset-bar card">', '<div class="preset-bar card" id="singlePresetBar">')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated index.html with Bulk UI")
