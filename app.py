from flask import Flask, render_template, request, send_file
from openpyxl import load_workbook
from datetime import datetime
import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
generated_file = "generated/updated_trim.xlsx"
generated_pdf = "generated/trim_sheet.pdf"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        regn = request.form['regn']
        pilot_weight = float(request.form['pilot_weight'])
        pax_weight = float(request.form['pax_weight'])
        fuel_left = float(request.form['fuel_left'])
        fuel_right = float(request.form['fuel_right'])

        wb = load_workbook('master_trim.xlsx')
        ws = wb.active

        # Your existing Excel processing code...
        ws["B1"] = datetime.now().strftime("%d/%m/%Y")
        ws["E2"] = regn

        if regn == "IAU":
            c5, e5 = 1173.96, 31.47
        elif regn == "NNN":
            c5, e5 = 1219, 31.6
        elif regn == "PSS":
            c5, e5 = 1201, 31.09
        else:
            c5, e5 = 0, 0

        ws["C5"] = round(c5, 2)
        ws["E5"] = round(e5, 2)
        ws["G5"] = round(c5 * e5, 2)

        ws["C6"] = round(pilot_weight, 2)
        ws["C7"] = round(pax_weight, 2)

        e6 = ws["E6"].value or 0
        e7 = ws["E7"].value or 0

        ws["G6"] = round(pilot_weight * e6, 2)
        ws["G7"] = round(pax_weight * e7, 2)

        ws["B18"] = round(c5 + pilot_weight + pax_weight, 2)
        ws["E11"] = round(ws["G5"].value + ws["G6"].value + ws["G7"].value, 2)

        ws["B13"] = round(fuel_left, 2)
        ws["B14"] = round(fuel_right, 2)
        ws["B15"] = round(fuel_left + fuel_right, 2)

        ws["C13"] = round(fuel_left * 1.58, 2)
        ws["C14"] = round(fuel_right * 1.58, 2)
        ws["C15"] = round(ws["C13"].value + ws["C14"].value, 2)

        e15 = ws["E15"].value or 0
        ws["G15"] = round(ws["C15"].value * e15, 2)

        ws["E12"] = round(ws["G15"].value, 2)
        ws["E13"] = round(ws["E11"].value + ws["E12"].value, 2)

        ws["C20"] = round(ws["C5"].value + ws["C6"].value + ws["C7"].value + ws["C13"].value + ws["C14"].value, 2)
        ws["G20"] = "Y" if ws["C20"].value < 1670 else "N"

        if ws["C20"].value and ws["E13"].value:
            ws["C21"] = round(ws["E13"].value / ws["C20"].value, 2)

        cg_val = ws["C21"].value
        ws["G21"] = "Y" if cg_val is not None and 31 <= cg_val <= 36.5 else "N"

        # Save to downloadable file
        os.makedirs("generated", exist_ok=True)
        wb.save(generated_file)

        # Create PDF version
        create_pdf(ws)
        
        # Prepare display data
        data = [[cell.value for cell in row] for row in ws.iter_rows(min_row=1, max_row=24, max_col=7)]
        return render_template("table.html", data=data, pdf_available=True)

    return render_template("index.html")

def create_pdf(worksheet):
    # Prepare data for PDF
    data = []
    for row in worksheet.iter_rows(min_row=1, max_row=24, max_col=7):
        data.append([str(cell.value) if cell.value is not None else "" for cell in row])

    # Create PDF
    doc = SimpleDocTemplate(generated_pdf, pagesize=landscape(A4))
    elements = []
    
    # Title
    styles = getSampleStyleSheet()
    title = Paragraph("Aircraft Trim Sheet", styles['Title'])
    elements.append(title)
    
    # Create table
    table = Table(data)
    
    # Add style
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ])
    table.setStyle(style)
    
    elements.append(table)
    doc.build(elements)

@app.route('/download_pdf')
def download_pdf():
    return send_file(generated_pdf, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)