import os
from fpdf import FPDF

class Report(FPDF):
    def header(self):
        filepath = os.path.dirname(os.path.abspath(__file__))
        logopath = os.path.join(filepath, "logo.png")

        self.image(logopath, 8, 8, w=80)
        self.ln(20)

    def footer(self):
        self.set_y(-18)
        document.set_font('helvetica', "B", 10)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align='C', border=True)
        



document = Report(orientation="landscape", format="A4", unit="mm")

document.alias_nb_pages()

document.set_auto_page_break(auto=True, margin=28)

document.add_page()

document.set_font('helvetica', size=16)

for i in range(1, 50):
    document.cell(20,10, f"line {i}", ln=True, border=True)


document.output("test.pdf")