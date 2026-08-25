import io
import xlsxwriter
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import ChartData
from pptx.dml.color import RGBColor
import os

LOGO_PATH = os.path.join("static", "logos", "credivex_logo.jpg")

def generate_excel_report(results):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    
    # 1. Data Sheet
    data_sheet = workbook.add_worksheet('Evaluation Data')
    header_format = workbook.add_format({'bold': True, 'bg_color': '#0f172a', 'font_color': 'white'})
    
    headers = ['Row', 'Annual Income', 'Loan Amount', 'Credit Score', 'DTI', 'Years Employed', 'Delinquencies', 'Verdict', 'Approval %', 'Risk Tier', 'Decision Margin']
    for col, h in enumerate(headers):
        data_sheet.write(0, col, h, header_format)
        
    for row_idx, res in enumerate(results, start=1):
        data_sheet.write(row_idx, 0, res['row'])
        data_sheet.write(row_idx, 1, res['inputs']['annual_income'])
        data_sheet.write(row_idx, 2, res['inputs']['loan_amount'])
        data_sheet.write(row_idx, 3, res['inputs']['credit_score'])
        data_sheet.write(row_idx, 4, res['inputs']['debt_to_income_ratio'])
        data_sheet.write(row_idx, 5, res['inputs']['years_employed'])
        data_sheet.write(row_idx, 6, res['inputs']['delinquencies_last_2yrs'])
        data_sheet.write(row_idx, 7, res['prediction'])
        data_sheet.write(row_idx, 8, res['approval_percentage'])
        data_sheet.write(row_idx, 9, res['risk_tier'])
        data_sheet.write(row_idx, 10, res['decision_margin'])
        
    # 2. Analytics Sheet
    chart_sheet = workbook.add_worksheet('Visual Analytics')
    
    # Add Logo
    if os.path.exists(LOGO_PATH):
        chart_sheet.insert_image('B2', LOGO_PATH, {'x_scale': 0.5, 'y_scale': 0.5})
        
    chart_sheet.write('B7', 'CREDIVEX Bulk Evaluation Analytics', workbook.add_format({'bold': True, 'font_size': 20, 'font_color': '#0f172a'}))
    
    # Hidden data sheet for charts
    cdata = workbook.add_worksheet('ChartData')
    cdata.hide()
    
    # Scatter Data
    scatter_app_x = []
    scatter_app_y = []
    scatter_den_x = []
    scatter_den_y = []

    # Helper to calculate brackets
    def get_ye_bucket(ye):
        if ye <= 2: return 0
        if ye <= 5: return 1
        if ye <= 10: return 2
        if ye <= 20: return 3
        return 4
    ye_labels = ['0-2 yrs', '3-5 yrs', '6-10 yrs', '11-20 yrs', '21+ yrs']
    ye_totals = [0]*5
    ye_approvals = [0]*5
    
    def get_loan_bucket(amt):
        if amt < 10000: return 0
        if amt < 20000: return 1
        if amt < 30000: return 2
        if amt < 50000: return 3
        if amt < 75000: return 4
        if amt < 100000: return 5
        if amt < 150000: return 6
        return 7
    loan_labels = ['<$10k','$10-20k','$20-30k','$30-50k','$50-75k','$75-100k','$100-150k','>$150k']
    loan_app = [0]*8
    loan_den = [0]*8
    
    for r in results:
        dti = r['inputs'].get('debt_to_income_ratio', 0) * 100
        score = r['inputs'].get('credit_score', 0)
        if r.get('is_approved'):
            scatter_app_x.append(dti)
            scatter_app_y.append(score)
        else:
            scatter_den_x.append(dti)
            scatter_den_y.append(score)

        ye = r['inputs'].get('years_employed', 0)
        idx = get_ye_bucket(ye)
        ye_totals[idx] += 1
        if r.get('is_approved'): ye_approvals[idx] += 1
        
        amt = r['inputs'].get('loan_amount', 0)
        l_idx = get_loan_bucket(amt)
        if r.get('is_approved'): loan_app[l_idx] += 1
        else: loan_den[l_idx] += 1
        
    ye_rates = [round((ye_approvals[i]/ye_totals[i])*100, 1) if ye_totals[i]>0 else 0 for i in range(5)]
    
    # Write Scatter Data
    cdata.write_column('H1', ['App DTI'] + scatter_app_x)
    cdata.write_column('I1', ['App Score'] + scatter_app_y)
    cdata.write_column('J1', ['Den DTI'] + scatter_den_x)
    cdata.write_column('K1', ['Den Score'] + scatter_den_y)

    cdata.write_column('A1', ['Years Employed'] + ye_labels)
    cdata.write_column('B1', ['Approval Rate'] + ye_rates)
    
    cdata.write_column('D1', ['Loan Amount'] + loan_labels)
    cdata.write_column('E1', ['Approved'] + loan_app)
    cdata.write_column('F1', ['Denied'] + loan_den)
    
    # ---------------- Chart 0: Scatter (DTI vs Credit Score) ----------------
    scatter = workbook.add_chart({'type': 'scatter'})
    if scatter_app_x:
        scatter.add_series({
            'name': 'Approved',
            'categories': f'=ChartData!$H$2:$H${len(scatter_app_x)+1}',
            'values':     f'=ChartData!$I$2:$I${len(scatter_app_y)+1}',
            'marker': {'type': 'circle', 'size': 5, 'border': {'color': '#059669'}, 'fill': {'color': '#059669'}}
        })
    if scatter_den_x:
        scatter.add_series({
            'name': 'Denied',
            'categories': f'=ChartData!$J$2:$J${len(scatter_den_x)+1}',
            'values':     f'=ChartData!$K$2:$K${len(scatter_den_y)+1}',
            'marker': {'type': 'circle', 'size': 5, 'border': {'color': '#dc2626'}, 'fill': {'color': '#dc2626'}}
        })
    scatter.set_title({'name': 'Decision Boundary: DTI vs Credit Score'})
    scatter.set_x_axis({'name': 'Debt-to-Income Ratio (%)'})
    scatter.set_y_axis({'name': 'Credit Score (FICO)'})
    chart_sheet.insert_chart('B9', scatter, {'x_scale': 1.2, 'y_scale': 1.1})

    # ---------------- Chart 1: Bar (Approval Rate) ----------------
    bar_chart = workbook.add_chart({'type': 'column'})
    bar_chart.add_series({
        'categories': '=ChartData!$A$2:$A$6',
        'values': '=ChartData!$B$2:$B$6',
        'fill': {'color': '#059669'}
    })
    bar_chart.set_title({'name': 'Approval Rate by Employment Tenure'})
    bar_chart.set_x_axis({'name': 'Years Employed'})
    bar_chart.set_y_axis({'name': 'Approval Rate (%)', 'max': 100})
    bar_chart.set_legend({'none': True})
    chart_sheet.insert_chart('L9', bar_chart, {'x_scale': 1.2, 'y_scale': 1.1})
    
    # ---------------- Chart 2: Histogram (Loan Amount) ----------------
    hist_chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})
    hist_chart.add_series({
        'name': 'Approved',
        'categories': '=ChartData!$D$2:$D$9',
        'values': '=ChartData!$E$2:$E$9',
        'fill': {'color': '#059669'}
    })
    hist_chart.add_series({
        'name': 'Denied',
        'categories': '=ChartData!$D$2:$D$9',
        'values': '=ChartData!$F$2:$F$9',
        'fill': {'color': '#dc2626'}
    })
    hist_chart.set_title({'name': 'Loan Amount Distribution'})
    hist_chart.set_x_axis({'name': 'Loan Amount ($)'})
    hist_chart.set_y_axis({'name': 'Number of Applications'})
    chart_sheet.insert_chart('B28', hist_chart, {'x_scale': 2.4, 'y_scale': 1.2})
    
    workbook.close()
    output.seek(0)
    return output

def generate_ppt_report(results):
    prs = Presentation()
    
    scatter_app_x = []
    scatter_app_y = []
    scatter_den_x = []
    scatter_den_y = []

    def get_ye_bucket(ye):
        if ye <= 2: return 0
        if ye <= 5: return 1
        if ye <= 10: return 2
        if ye <= 20: return 3
        return 4
    ye_labels = ['0-2 yrs', '3-5 yrs', '6-10 yrs', '11-20 yrs', '21+ yrs']
    ye_totals = [0]*5
    ye_approvals = [0]*5
    
    def get_loan_bucket(amt):
        if amt < 10000: return 0
        if amt < 20000: return 1
        if amt < 30000: return 2
        if amt < 50000: return 3
        if amt < 75000: return 4
        if amt < 100000: return 5
        if amt < 150000: return 6
        return 7
    loan_labels = ['<$10k','$10-20k','$20-30k','$30-50k','$50-75k','$75-100k','$100-150k','>$150k']
    loan_app = [0]*8
    loan_den = [0]*8
    
    for r in results:
        dti = r['inputs'].get('debt_to_income_ratio', 0) * 100
        score = r['inputs'].get('credit_score', 0)
        if r.get('is_approved'):
            scatter_app_x.append(dti)
            scatter_app_y.append(score)
        else:
            scatter_den_x.append(dti)
            scatter_den_y.append(score)

        ye = r['inputs'].get('years_employed', 0)
        idx = get_ye_bucket(ye)
        ye_totals[idx] += 1
        if r.get('is_approved'): ye_approvals[idx] += 1
        
        amt = r['inputs'].get('loan_amount', 0)
        l_idx = get_loan_bucket(amt)
        if r.get('is_approved'): loan_app[l_idx] += 1
        else: loan_den[l_idx] += 1
        
    ye_rates = [round((ye_approvals[i]/ye_totals[i])*100, 1) if ye_totals[i]>0 else 0 for i in range(5)]
    
    # ---------------- Slide 1: Title ----------------
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "CREDIVEX Bulk Evaluation Analytics"
    subtitle.text = f"Total Processed: {len(results)}\nNative Chart Report"
    
    if os.path.exists(LOGO_PATH):
        slide.shapes.add_picture(LOGO_PATH, Inches(4), Inches(0.5), height=Inches(1.5))
        
    x, y, cx, cy = Inches(1), Inches(1.5), Inches(8), Inches(5)

    # ---------------- Slide 2: Scatter Chart ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Decision Boundary: DTI vs Credit Score"
    
    from pptx.chart.data import XyChartData
    chart_data = XyChartData()
    
    if scatter_app_x:
        series1 = chart_data.add_series('Approved')
        for x_val, y_val in zip(scatter_app_x, scatter_app_y):
            series1.add_data_point(x_val, y_val)
            
    if scatter_den_x:
        series2 = chart_data.add_series('Denied')
        for x_val, y_val in zip(scatter_den_x, scatter_den_y):
            series2.add_data_point(x_val, y_val)
        
    chart = slide.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER, x, y, cx, cy, chart_data).chart
    chart.has_title = False
    
    chart.category_axis.has_title = True
    chart.category_axis.axis_title.text_frame.text = 'Debt-to-Income Ratio (%)'
    chart.value_axis.has_title = True
    chart.value_axis.axis_title.text_frame.text = 'Credit Score (FICO)'
    
    if scatter_app_x:
        chart.series[0].marker.format.fill.solid()
        chart.series[0].marker.format.fill.fore_color.rgb = RGBColor(5, 150, 105)
    if scatter_den_x:
        s_idx = 1 if scatter_app_x else 0
        chart.series[s_idx].marker.format.fill.solid()
        chart.series[s_idx].marker.format.fill.fore_color.rgb = RGBColor(220, 38, 38)

    # ---------------- Slide 3: Bar Chart ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Approval Rate by Employment Tenure"
    
    chart_data = ChartData()
    chart_data.categories = ye_labels
    chart_data.add_series('Approval Rate', tuple(ye_rates))
    
    chart = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data).chart
    chart.has_title = False 
    chart.category_axis.has_title = True
    chart.category_axis.axis_title.text_frame.text = 'Years Employed'
    chart.value_axis.has_title = True
    chart.value_axis.axis_title.text_frame.text = 'Approval Rate (%)'
    
    chart.series[0].format.fill.solid()
    chart.series[0].format.fill.fore_color.rgb = RGBColor(5, 150, 105)
    
    # ---------------- Slide 4: Histogram ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Loan Amount Distribution"
    
    chart_data = ChartData()
    chart_data.categories = loan_labels
    chart_data.add_series('Approved', tuple(loan_app))
    chart_data.add_series('Denied', tuple(loan_den))
    
    chart = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_STACKED, x, y, cx, cy, chart_data).chart
    chart.has_title = False
    chart.category_axis.has_title = True
    chart.category_axis.axis_title.text_frame.text = 'Loan Amount ($)'
    chart.value_axis.has_title = True
    chart.value_axis.axis_title.text_frame.text = 'Number of Applications'
    
    chart.series[0].format.fill.solid()
    chart.series[0].format.fill.fore_color.rgb = RGBColor(5, 150, 105) 
    chart.series[1].format.fill.solid()
    chart.series[1].format.fill.fore_color.rgb = RGBColor(220, 38, 38)
    
    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    return output
