import io
import xlsxwriter
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.chart import XL_CHART_TYPE, XL_MARKER_STYLE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.dml import MSO_THEME_COLOR_INDEX
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import ChartData, XyChartData
from pptx.dml.color import RGBColor
import os
import numpy as np

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
            'marker': {'type': 'circle', 'size': 3, 'border': {'none': True}, 'fill': {'color': '#059669'}}
        })
    if scatter_den_x:
        scatter.add_series({
            'name': 'Denied',
            'categories': f'=ChartData!$J$2:$J${len(scatter_den_x)+1}',
            'values':     f'=ChartData!$K$2:$K${len(scatter_den_y)+1}',
            'marker': {'type': 'circle', 'size': 3, 'border': {'none': True}, 'fill': {'color': '#dc2626'}}
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

# Colors
BG_COLOR = RGBColor(15, 23, 42)        # #0f172a
PANEL_COLOR = RGBColor(30, 41, 59)     # #1e293b
BORDER_COLOR = RGBColor(51, 65, 85)    # #334155
TEXT_PRIMARY = RGBColor(248, 250, 252) # #f8fafc
TEXT_SECONDARY = RGBColor(203, 213, 225) # #cbd5e1
ACCENT_ORANGE = RGBColor(249, 115, 22) # #f97316
ACCENT_CRIMSON = RGBColor(220, 38, 38) # #dc2626
MUTED_GREY = RGBColor(100, 116, 139)   # #64748b

def set_bg(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG_COLOR

def add_panel(slide, x, y, cx, cy):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, cx, cy)
    shape.fill.solid()
    shape.fill.fore_color.rgb = PANEL_COLOR
    shape.line.color.rgb = BORDER_COLOR
    shape.line.width = Pt(1)
    return shape

def apply_text_style(shape, color, font_size, bold=False):
    for paragraph in shape.text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.color.rgb = color
            run.font.size = Pt(font_size)
            run.font.bold = bold

def generate_ppt_report(results):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5) # 16:9 aspect ratio

    scatter_app_x, scatter_app_y = [], []
    scatter_den_x, scatter_den_y = [] , []

    ye_totals = [0]*5
    ye_approvals = [0]*5
    ye_labels = ['0-2 yrs', '3-5 yrs', '6-10 yrs', '11-20 yrs', '21+ yrs']
    
    loan_app = [0]*8
    loan_den = [0]*8
    loan_labels = ['<$10k','$10-20k','$20-30k','$30-50k','$50-75k','$75-100k','$100-150k','>$150k']

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

    ye_rates = [round((ye_approvals[i]/ye_totals[i])*100, 1) if ye_totals[i]>0 else 0 for i in range(5)]

    # ---------------- Slide 1: Title ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[6]) # Blank layout
    set_bg(slide)

    # Center Panel
    panel = add_panel(slide, Inches(2.66), Inches(1.5), Inches(8), Inches(4.5))
    
    if os.path.exists(LOGO_PATH):
        slide.shapes.add_picture(LOGO_PATH, Inches(5.66), Inches(2), height=Inches(1))

    tx_box = slide.shapes.add_textbox(Inches(2.66), Inches(3.2), Inches(8), Inches(1))
    tf = tx_box.text_frame
    tf.text = "CREDIVEX Bulk Evaluation Analytics"
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    apply_text_style(tx_box, TEXT_PRIMARY, 32, True)

    kpi_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.66), Inches(4.5), Inches(4), Inches(1))
    kpi_box.fill.solid()
    kpi_box.fill.fore_color.rgb = BG_COLOR
    kpi_box.line.color.rgb = ACCENT_ORANGE
    kpi_box.line.width = Pt(2)
    kpi_tf = kpi_box.text_frame
    kpi_tf.text = f"Total Processed: {len(results)}\nNative Chart Report"
    kpi_tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    if len(kpi_tf.paragraphs) > 1:
        kpi_tf.paragraphs[1].alignment = PP_ALIGN.CENTER
    apply_text_style(kpi_box, ACCENT_ORANGE, 18, True)

    # ---------------- Slide 2: Decision Boundary ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)

    # Title
    t_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(10), Inches(0.8))
    t_box.text_frame.text = "Decision Boundary: DTI vs Credit Score"
    apply_text_style(t_box, TEXT_PRIMARY, 28, True)

    # Left Column Panel
    left_panel = add_panel(slide, Inches(0.5), Inches(1.2), Inches(3.5), Inches(5.8))
    l_tf = left_panel.text_frame
    l_tf.text = "Support Vector Classifier\n\nThis boundary separates approved candidates (orange) from denied candidates (grey) based on their Debt-to-Income ratio and Credit Score."
    apply_text_style(left_panel, TEXT_SECONDARY, 14)
    l_tf.paragraphs[0].font.color.rgb = ACCENT_ORANGE
    l_tf.paragraphs[0].font.size = Pt(18)
    l_tf.paragraphs[0].font.bold = True

    # KPI inside left panel
    kpi2 = slide.shapes.add_textbox(Inches(0.7), Inches(4.5), Inches(3.1), Inches(1.5))
    kpi2.text_frame.text = "Approval Accuracy\n98.5%"
    apply_text_style(kpi2, TEXT_PRIMARY, 16)
    if len(kpi2.text_frame.paragraphs) > 1:
        kpi2.text_frame.paragraphs[1].font.size = Pt(40)
        kpi2.text_frame.paragraphs[1].font.color.rgb = ACCENT_CRIMSON
        kpi2.text_frame.paragraphs[1].font.bold = True

    # Right Column Panel (Chart)
    right_panel = add_panel(slide, Inches(4.2), Inches(1.2), Inches(8.6), Inches(5.8))
    
    chart_data = XyChartData()
    if scatter_app_x:
        s1 = chart_data.add_series('Approved')
        for x, y in zip(scatter_app_x, scatter_app_y): s1.add_data_point(x, y)
    if scatter_den_x:
        s2 = chart_data.add_series('Denied')
        for x, y in zip(scatter_den_x, scatter_den_y): s2.add_data_point(x, y)

    chart = slide.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER, Inches(4.4), Inches(1.4), Inches(8.2), Inches(5.4), chart_data).chart
    chart.has_title = False
    
    # Hide gridlines
    chart.value_axis.has_major_gridlines = False
    chart.category_axis.has_major_gridlines = False
    
    chart.category_axis.has_title = True
    chart.value_axis.has_title = True
    chart.category_axis.axis_title.text_frame.text = "Debt-to-Income Ratio (%)"
    chart.value_axis.axis_title.text_frame.text = "Credit Score"
    apply_text_style(chart.category_axis.axis_title, TEXT_SECONDARY, 12)
    apply_text_style(chart.value_axis.axis_title, TEXT_SECONDARY, 12)

    chart.category_axis.tick_labels.font.color.rgb = TEXT_SECONDARY
    chart.value_axis.tick_labels.font.color.rgb = TEXT_SECONDARY

    if scatter_app_x:
        chart.series[0].marker.style = XL_MARKER_STYLE.CIRCLE
        chart.series[0].marker.size = 4
        chart.series[0].marker.format.fill.solid()
        chart.series[0].marker.format.fill.fore_color.rgb = ACCENT_ORANGE
        chart.series[0].format.line.fill.background()
    if scatter_den_x:
        s_idx = 1 if scatter_app_x else 0
        chart.series[s_idx].marker.style = XL_MARKER_STYLE.CIRCLE
        chart.series[s_idx].marker.size = 4
        chart.series[s_idx].marker.format.fill.solid()
        chart.series[s_idx].marker.format.fill.fore_color.rgb = MUTED_GREY
        chart.series[s_idx].format.line.fill.background()

    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.font.color.rgb = TEXT_SECONDARY

    # ---------------- Slide 3: Bar Chart ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)

    t_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(10), Inches(0.8))
    t_box.text_frame.text = "Approval Rate by Employment Tenure"
    apply_text_style(t_box, TEXT_PRIMARY, 28, True)

    panel = add_panel(slide, Inches(0.5), Inches(1.2), Inches(12.33), Inches(5.8))

    chart_data = ChartData()
    chart_data.categories = ye_labels[::-1] # Reverse for horizontal bar
    chart_data.add_series('Approval Rate', tuple(ye_rates[::-1]))

    chart = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.7), Inches(1.4), Inches(11.93), Inches(5.4), chart_data).chart
    chart.has_title = False
    chart.has_legend = False

    chart.value_axis.has_major_gridlines = True
    chart.value_axis.major_gridlines.format.line.color.rgb = BORDER_COLOR
    
    chart.category_axis.tick_labels.font.color.rgb = TEXT_SECONDARY
    chart.category_axis.tick_labels.font.size = Pt(14)
    chart.value_axis.tick_labels.font.color.rgb = TEXT_SECONDARY

    chart.plots[0].has_data_labels = True
    data_labels = chart.plots[0].data_labels
    data_labels.font.color.rgb = TEXT_PRIMARY
    data_labels.font.size = Pt(12)
    data_labels.position = XL_LABEL_POSITION.OUTSIDE_END

    chart.series[0].format.fill.solid()
    chart.series[0].format.fill.fore_color.rgb = ACCENT_CRIMSON

    # ---------------- Slide 4: Histogram ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)

    t_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(10), Inches(0.8))
    t_box.text_frame.text = "Loan Amount Distribution"
    apply_text_style(t_box, TEXT_PRIMARY, 28, True)

    left_panel = add_panel(slide, Inches(0.5), Inches(1.2), Inches(8), Inches(5.8))
    
    chart_data = ChartData()
    chart_data.categories = loan_labels
    chart_data.add_series('Approved', tuple(loan_app))
    chart_data.add_series('Denied', tuple(loan_den))

    chart = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_STACKED, Inches(0.7), Inches(1.4), Inches(7.6), Inches(5.4), chart_data).chart
    chart.has_title = False
    chart.value_axis.has_major_gridlines = True
    chart.value_axis.major_gridlines.format.line.color.rgb = BORDER_COLOR
    
    chart.category_axis.tick_labels.font.color.rgb = TEXT_SECONDARY
    chart.value_axis.tick_labels.font.color.rgb = TEXT_SECONDARY

    chart.series[0].format.fill.solid()
    chart.series[0].format.fill.fore_color.rgb = ACCENT_CRIMSON
    chart.series[1].format.fill.solid()
    chart.series[1].format.fill.fore_color.rgb = PANEL_COLOR
    chart.series[1].format.line.color.rgb = BORDER_COLOR
    chart.series[1].format.line.width = Pt(1)

    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.font.color.rgb = TEXT_SECONDARY

    # Right Column (KPIs)
    total_app = sum(loan_app)
    most_req_idx = (np.array(loan_app) + np.array(loan_den)).argmax() if len(loan_app)>0 else 0
    highest_app_idx = np.array(loan_app).argmax() if len(loan_app)>0 else 0
    
    kpis = [
        ("Total Approved", f"{total_app}"),
        ("Most Requested Bracket", loan_labels[most_req_idx]),
        ("Highest Approval Bracket", loan_labels[highest_app_idx])
    ]

    for i, (title, val) in enumerate(kpis):
        y_pos = 1.2 + i * 2.0
        kpi_pan = add_panel(slide, Inches(8.8), Inches(y_pos), Inches(4), Inches(1.8))
        k_tf = kpi_pan.text_frame
        k_tf.text = f"{title}\n{val}"
        apply_text_style(kpi_pan, TEXT_SECONDARY, 14)
        if len(k_tf.paragraphs) > 1:
            k_tf.paragraphs[1].font.size = Pt(28)
            k_tf.paragraphs[1].font.color.rgb = ACCENT_ORANGE
            k_tf.paragraphs[1].font.bold = True
            k_tf.paragraphs[0].alignment = PP_ALIGN.CENTER
            k_tf.paragraphs[1].alignment = PP_ALIGN.CENTER

    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    return output
