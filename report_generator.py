import io
import os
import re
import numpy as np
import openpyxl
from pptx import Presentation
from pptx.chart.data import ChartData, XyChartData
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt
from pptx.dml.color import RGBColor

def get_ye_bucket(ye):
    if ye <= 2: return 0
    if ye <= 5: return 1
    if ye <= 10: return 2
    if ye <= 20: return 3
    return 4

def get_loan_bucket(amt):
    if amt < 10000: return 0
    if amt < 20000: return 1
    if amt < 30000: return 2
    if amt < 50000: return 3
    if amt < 75000: return 4
    if amt < 100000: return 5
    if amt < 150000: return 6
    return 7

def generate_excel_report(results):
    TEMPLATE_PATH = os.path.join("static", "templates", "template.xlsx")
    wb = openpyxl.load_workbook(TEMPLATE_PATH)
    
    ws_data = wb['Evaluation Data']
    if ws_data.max_row > 1:
        ws_data.delete_rows(2, ws_data.max_row - 1)
        
    for row_idx, res in enumerate(results, start=2):
        ws_data.cell(row=row_idx, column=1, value=res.get('row', row_idx-1))
        ws_data.cell(row=row_idx, column=2, value=res['inputs'].get('annual_income', 0))
        ws_data.cell(row=row_idx, column=3, value=res['inputs'].get('loan_amount', 0))
        ws_data.cell(row=row_idx, column=4, value=res['inputs'].get('credit_score', 0))
        ws_data.cell(row=row_idx, column=5, value=res['inputs'].get('debt_to_income_ratio', 0))
        ws_data.cell(row=row_idx, column=6, value=res['inputs'].get('years_employed', 0))
        ws_data.cell(row=row_idx, column=7, value=res['inputs'].get('delinquencies_last_2yrs', 0))
        ws_data.cell(row=row_idx, column=8, value=res.get('prediction', ''))
        ws_data.cell(row=row_idx, column=9, value=res.get('approval_percentage', ''))
        ws_data.cell(row=row_idx, column=10, value=res.get('risk_tier', ''))
        
    scatter_app_x, scatter_app_y = [], []
    scatter_den_x, scatter_den_y = [], []
    ye_totals, ye_approvals = [0]*5, [0]*5
    ye_labels = ['0-2 yrs', '3-5 yrs', '6-10 yrs', '11-20 yrs', '21+ yrs']
    loan_app, loan_den = [0]*8, [0]*8
    loan_labels = ['<$10k', '$10-20k', '$20-30k', '$30-50k', '$50-75k', '$75-100k', '$100-150k', '>$150k']
    
    for r in results:
        dti = r['inputs'].get('debt_to_income_ratio', 0) * 100
        score = r['inputs'].get('credit_score', 0)
        is_app = r.get('is_approved', False)
        if is_app:
            scatter_app_x.append(dti)
            scatter_app_y.append(score)
        else:
            scatter_den_x.append(dti)
            scatter_den_y.append(score)
            
        ye = r['inputs'].get('years_employed', 0)
        idx = get_ye_bucket(ye)
        ye_totals[idx] += 1
        if is_app: ye_approvals[idx] += 1
        
        amt = r['inputs'].get('loan_amount', 0)
        l_idx = get_loan_bucket(amt)
        if is_app: loan_app[l_idx] += 1
        else: loan_den[l_idx] += 1
        
    ye_rates = [round((ye_approvals[i] / ye_totals[i]) * 100, 1) if ye_totals[i] > 0 else 0 for i in range(5)]
    
    ws_cdata = wb['ChartData']
    if ws_cdata.max_row > 1:
        ws_cdata.delete_rows(2, ws_cdata.max_row - 1)
        
    for i in range(5):
        ws_cdata.cell(row=i+2, column=1, value=ye_labels[i])
        ws_cdata.cell(row=i+2, column=2, value=ye_rates[i])
        
    for i in range(8):
        ws_cdata.cell(row=i+2, column=4, value=loan_labels[i])
        ws_cdata.cell(row=i+2, column=5, value=loan_app[i])
        ws_cdata.cell(row=i+2, column=6, value=loan_den[i])
        
    for i, (x, y) in enumerate(zip(scatter_app_x, scatter_app_y)):
        ws_cdata.cell(row=i+2, column=8, value=x)
        ws_cdata.cell(row=i+2, column=9, value=y)
        
    for i, (x, y) in enumerate(zip(scatter_den_x, scatter_den_y)):
        ws_cdata.cell(row=i+2, column=10, value=x)
        ws_cdata.cell(row=i+2, column=11, value=y)
        
    ws_charts = wb['Visual Analytics']
    for chart in ws_charts._charts:
        if chart.__class__.__name__ == 'ScatterChart':
            ref_app = max(len(scatter_app_x) + 1, 2)
            ref_den = max(len(scatter_den_x) + 1, 2)
            for s in chart.series:
                name = s.tx.v if (hasattr(s, 'tx') and s.tx and hasattr(s.tx, 'v')) else None
                if name == 'Approved':
                    if hasattr(s, 'xVal') and s.xVal and hasattr(s.xVal, 'numRef'):
                        s.xVal.numRef.f = re.sub(r'\$\d+$', f'${ref_app}', s.xVal.numRef.f)
                    if hasattr(s, 'yVal') and s.yVal and hasattr(s.yVal, 'numRef'):
                        s.yVal.numRef.f = re.sub(r'\$\d+$', f'${ref_app}', s.yVal.numRef.f)
                elif name == 'Denied':
                    if hasattr(s, 'xVal') and s.xVal and hasattr(s.xVal, 'numRef'):
                        s.xVal.numRef.f = re.sub(r'\$\d+$', f'${ref_den}', s.xVal.numRef.f)
                    if hasattr(s, 'yVal') and s.yVal and hasattr(s.yVal, 'numRef'):
                        s.yVal.numRef.f = re.sub(r'\$\d+$', f'${ref_den}', s.yVal.numRef.f)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def generate_ppt_report(results):
    TEMPLATE_PATH = os.path.join("static", "templates", "template.pptx")
    prs = Presentation(TEMPLATE_PATH)
    
    scatter_app_x, scatter_app_y = [], []
    scatter_den_x, scatter_den_y = [], []
    ye_totals, ye_approvals = [0]*5, [0]*5
    ye_labels = ['0-2 yrs', '3-5 yrs', '6-10 yrs', '11-20 yrs', '21+ yrs']
    loan_app, loan_den = [0]*8, [0]*8
    loan_labels = ['<$10k', '$10-20k', '$20-30k', '$30-50k', '$50-75k', '$75-100k', '$100-150k', '>$150k']
    
    for r in results:
        dti = r['inputs'].get('debt_to_income_ratio', 0) * 100
        score = r['inputs'].get('credit_score', 0)
        is_app = r.get('is_approved', False)
        if is_app:
            scatter_app_x.append(dti)
            scatter_app_y.append(score)
        else:
            scatter_den_x.append(dti)
            scatter_den_y.append(score)
            
        ye = r['inputs'].get('years_employed', 0)
        idx = get_ye_bucket(ye)
        ye_totals[idx] += 1
        if is_app: ye_approvals[idx] += 1
        
        amt = r['inputs'].get('loan_amount', 0)
        l_idx = get_loan_bucket(amt)
        if is_app: loan_app[l_idx] += 1
        else: loan_den[l_idx] += 1
        
    ye_rates = [round((ye_approvals[i] / ye_totals[i]) * 100, 1) if ye_totals[i] > 0 else 0 for i in range(5)]
    total_app = sum(loan_app)
    arr_total = np.array(loan_app) + np.array(loan_den)
    most_req_idx = int(arr_total.argmax()) if arr_total.sum() > 0 else 0
    highest_app_idx = int(np.array(loan_app).argmax()) if total_app > 0 else 0
    
    s1 = prs.slides[0]
    for shape in s1.shapes:
        if shape.has_text_frame and "Total Processed:" in shape.text:
            for p in shape.text_frame.paragraphs:
                if "Total Processed:" in p.text:
                    p.text = f"Total Processed: {len(results)}"
                    p.font.color.rgb = RGBColor(5, 150, 105)
                    p.font.size = Pt(18)
                    p.font.bold = True
                    p.alignment = PP_ALIGN.CENTER
            
    s2 = prs.slides[1]
    for shape in s2.shapes:
        if shape.has_chart:
            chart = shape.chart
            new_data = XyChartData()
            if scatter_app_x:
                s = new_data.add_series('Approved')
                for xv, yv in zip(scatter_app_x, scatter_app_y):
                    s.add_data_point(xv, yv)
            if scatter_den_x:
                s = new_data.add_series('Denied')
                for xv, yv in zip(scatter_den_x, scatter_den_y):
                    s.add_data_point(xv, yv)
            chart.replace_data(new_data)
            
    s3 = prs.slides[2]
    for shape in s3.shapes:
        if shape.has_chart:
            chart = shape.chart
            new_data = ChartData()
            new_data.categories = ye_labels[::-1]
            new_data.add_series('Approval Rate', tuple(ye_rates[::-1]))
            chart.replace_data(new_data)
            
    s4 = prs.slides[3]
    for shape in s4.shapes:
        if shape.has_chart:
            chart = shape.chart
            new_data = ChartData()
            new_data.categories = loan_labels
            new_data.add_series('Approved', tuple(loan_app))
            new_data.add_series('Denied', tuple(loan_den))
            chart.replace_data(new_data)
            
        elif shape.has_text_frame:
            if "Total Approved" in shape.text:
                if len(shape.text_frame.paragraphs) > 1:
                    p = shape.text_frame.paragraphs[1]
                    p.text = f"{total_app}"
                    p.font.color.rgb = RGBColor(5, 150, 105)
                    p.font.size = Pt(28)
                    p.font.bold = True
                    p.alignment = PP_ALIGN.CENTER
            elif "Most Requested Bracket" in shape.text:
                if len(shape.text_frame.paragraphs) > 1:
                    p = shape.text_frame.paragraphs[1]
                    p.text = f"{loan_labels[most_req_idx]}"
                    p.font.color.rgb = RGBColor(37, 99, 235)
                    p.font.size = Pt(28)
                    p.font.bold = True
                    p.alignment = PP_ALIGN.CENTER
            elif "Highest Approval Bracket" in shape.text:
                if len(shape.text_frame.paragraphs) > 1:
                    p = shape.text_frame.paragraphs[1]
                    p.text = f"{loan_labels[highest_app_idx]}"
                    p.font.color.rgb = RGBColor(234, 179, 8)
                    p.font.size = Pt(28)
                    p.font.bold = True
                    p.alignment = PP_ALIGN.CENTER

    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    return output
