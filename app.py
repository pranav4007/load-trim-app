from flask import Flask, render_template, request, send_file
from openpyxl import load_workbook
from datetime import datetime
import os

app = Flask(__name__)
generated_file = "generated/updated_trim.xlsx"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        regn = request.form['regn']
        pilot_weight = float(request.form['pilot_weight_lbs'])
        pax_weight = float(request.form['pax_weight_lbs'])
        fuel_left = float(request.form['fuel_left'])
        fuel_right = float(request.form['fuel_right'])

        wb = load_workbook('master_trim.xlsx')
        ws = wb.active

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

        # Save to downloadable Excel file
        os.makedirs("generated", exist_ok=True)
        wb.save(generated_file)

        # Prepare display data for table preview
        data = [[cell.value for cell in row] for row in ws.iter_rows(min_row=1, max_row=24, max_col=7)]
        return render_template("table.html", data=data, excel_available=True)

    return render_template("index.html")

@app.route('/download_excel')
def download_excel():
    return send_file(generated_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
