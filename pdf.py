from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def generate_PDF(name):
    pdfmetrics.registerFont(TTFont('GreatVibes', 'Great_Vibes,Lobster/Great_Vibes/GreatVibes-Regular.ttf'))
    name_font = 'GreatVibes'

    WIDTH, HEIGHT = landscape(A4)
    c = canvas.Canvas("certificate_filled.pdf", pagesize=(WIDTH, HEIGHT))

    c.setFillColor(HexColor("#fdf8e2"))
    c.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)

    c.setLineWidth(7)
    c.setStrokeColor(HexColor("#bfa14a"))
    c.roundRect(18*mm, 18*mm, WIDTH-36*mm, HEIGHT-36*mm, 18, fill=0, stroke=1)
    c.setLineWidth(2)
    c.setStrokeColor(HexColor("#fffde4"))
    c.roundRect(22*mm, 22*mm, WIDTH-44*mm, HEIGHT-44*mm, 14, fill=0, stroke=1)

    king_x = WIDTH/2
    king_y = HEIGHT-32*mm
    c.setFillColor(HexColor("#bfa14a"))
    c.setStrokeColor(HexColor("#bfa14a"))
    c.setLineWidth(3)

    c.line(king_x-7*mm, king_y+7*mm, king_x, king_y+14*mm)
    c.line(king_x+7*mm, king_y+7*mm, king_x, king_y+14*mm)
    c.line(king_x-7*mm, king_y+7*mm, king_x+7*mm, king_y+7*mm)
    c.circle(king_x, king_y+14*mm, 2.5*mm, fill=1, stroke=0)

    c.rect(king_x-2*mm, king_y+2*mm, 4*mm, 5*mm, fill=1, stroke=0)

    c.roundRect(king_x-6*mm, king_y-10*mm, 12*mm, 18*mm, 4, fill=1, stroke=0)

    c.setLineWidth(1.2)
    c.line(king_x, king_y+17*mm, king_x, king_y+22*mm)
    c.line(king_x-2*mm, king_y+19.5*mm, king_x+2*mm, king_y+19.5*mm)


    c.setFillColor(HexColor("#22223b"))
    c.drawCentredString(WIDTH/2+2, HEIGHT-54*mm-2, "Certificate of Grandmaster")
    c.setFillColor(HexColor("#bfa14a"))
    c.drawCentredString(WIDTH/2, HEIGHT-54*mm, "Certificate of Grandmaster")

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(HexColor("#22223b"))
    c.drawCentredString(WIDTH/2, HEIGHT-72*mm, "This certifies that")

    c.setFont(name_font, 36)
    name_width = pdfmetrics.stringWidth(name, name_font, 36)
    field_pad = 16*mm  # уменьшенные отступы по бокам
    field_w = name_width + field_pad
    field_h = 2*mm
    field_x = WIDTH/2 - field_w/2
    field_y = HEIGHT-105*mm

    c.setFillColor(HexColor("#bfa14a"))

    c.roundRect(field_x+3, field_y-3, field_w, field_h, 12, fill=1, stroke=0)

    c.setFillColor(Color(1,1,1,alpha=0.92))
    c.roundRect(field_x, field_y, field_w, field_h, 12, fill=1, stroke=0)

    c.setFont(name_font, 36)
    c.setFillColor(HexColor("#22223b"))
    c.drawCentredString(WIDTH/2, field_y + field_h/2 + 8, name)


    c.setFillColor(HexColor("#bfa14a"))
    c.rect(field_x-18*mm, field_y+field_h/2-2*mm, 16*mm, 4*mm, fill=1, stroke=0)
    c.rect(field_x+field_w+2*mm, field_y+field_h/2-2*mm, 16*mm, 4*mm, fill=1, stroke=0)


    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(HexColor("#22223b"))
    c.drawCentredString(WIDTH/2, 46*mm, "Awarded by the Chess Federation")


    c.setFont("Helvetica", 13)
    c.setFillColor(HexColor("#22223b"))
    c.drawCentredString(WIDTH/2, 34*mm, f"Date: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

    c.showPage()
    c.save()
    #print("Готово: certificate_filled.pdf")
