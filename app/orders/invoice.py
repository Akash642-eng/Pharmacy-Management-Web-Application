from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.lib.units import cm
import io
from datetime import datetime

PRIMARY_BLUE = HexColor("#0F172A") 
ACCENT_BLUE = HexColor("#3B82F6") 
LIGHT_GRAY = HexColor("#F8FAFC")
BORDER_GRAY = HexColor("#E2E8F0")
TEXT_DIM = HexColor("#64748B")
WATERMARK_COLOR = HexColor("#E0E7FF")

LEFT_MARGIN = 40
RIGHT_MARGIN = 40

def generate_invoice_pdf(order):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    def add_watermark(can, text):
        can.saveState()
        can.setFillColor(WATERMARK_COLOR)
        can.setFont("Helvetica-Bold", 85)
        can.translate(width/2, height/2) 
        can.rotate(45) 
        can.drawCentredString(0, 0, text)
        can.restoreState()
    
    add_watermark(pdf, "MARUTI PHARMACY")
    
    pdf.setFillColor(PRIMARY_BLUE)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(LEFT_MARGIN, height - 60, "MARUTI PHARMACY")
    
    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(TEXT_DIM)
    header_info = "DL No: 20B/1234/2026 | GSTIN: 29ABCDE1234F1Z5 | FSSAI: 12345678901234"
    pdf.drawString(LEFT_MARGIN, height - 75, header_info)

    pdf.setFillColor(ACCENT_BLUE)
    pdf.roundRect(width - 180, height - 65, 140, 22, 4, fill=1, stroke=0)
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(width - 110, height - 58, "RETAIL TAX INVOICE")

    y = height - 110
    pdf.setStrokeColor(BORDER_GRAY)
    pdf.setLineWidth(0.8) 
    pdf.line(LEFT_MARGIN, y, width - RIGHT_MARGIN, y)
    
    y -= 25 
    pdf.setFont("Helvetica-Bold", 10) 
    pdf.setFillColor(PRIMARY_BLUE)
    pdf.drawString(LEFT_MARGIN, y, "CUSTOMER ADDRESS")
    pdf.drawRightString(width - RIGHT_MARGIN, y, "BILLING DETAILS")
    
    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(black)

    address = getattr(order, 'address', "Local Sale")[:45]
    phone = getattr(order, 'phone', "N/A")
    
    pdf.drawString(LEFT_MARGIN, y - 18, f"Address: {address}")
    pdf.drawString(LEFT_MARGIN, y - 31, f"Contact: {phone}")

    pdf.drawRightString(width - RIGHT_MARGIN, y - 18, f"Invoice: {order.invoice_number}")
    pdf.drawRightString(width - RIGHT_MARGIN, y - 31, f"Date: {order.created_at.strftime('%d-%m-%Y %H:%M')}")
    pdf.drawRightString(width - RIGHT_MARGIN, y - 44, f"Payment: UPI")


    y -= 75
    pdf.setFillColor(PRIMARY_BLUE)
    pdf.rect(LEFT_MARGIN, y, width - (LEFT_MARGIN + RIGHT_MARGIN), 26, fill=1, stroke=0) # Taller header
    
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(LEFT_MARGIN + 5, y + 9, "DESCRIPTION")
    pdf.drawString(LEFT_MARGIN + 155, y + 9, "HSN")
    pdf.drawString(LEFT_MARGIN + 200, y + 9, "BATCH")
    pdf.drawString(LEFT_MARGIN + 255, y + 9, "EXP")
    pdf.drawCentredString(LEFT_MARGIN + 315, y + 9, "QTY")
    pdf.drawRightString(width - RIGHT_MARGIN - 65, y + 9, "RATE")
    pdf.drawRightString(width - RIGHT_MARGIN - 5, y + 9, "AMOUNT")


    y -= 25 
    pdf.setFillColor(black)
    pdf.setFont("Helvetica", 9)
    grand_total = 0 
    
    for item in order.items:
        amount = item.quantity * item.price 
        grand_total += amount
        
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(LEFT_MARGIN + 5, y - 12, item.product.name[:30])
        pdf.setFont("Helvetica", 9)
        
        pdf.drawString(LEFT_MARGIN + 155, y - 12, "300490")
        pdf.drawString(LEFT_MARGIN + 200, y - 12, "BT772X")
        pdf.drawString(LEFT_MARGIN + 255, y - 12, "12/2027")
        
        pdf.drawCentredString(LEFT_MARGIN + 315, y - 12, str(item.quantity))
        pdf.drawRightString(width - RIGHT_MARGIN - 70, y - 12, f"{item.price:.2f}")
        pdf.drawRightString(width - RIGHT_MARGIN - 5, y - 12, f"{amount:.2f}")
        
        y -= 25 # Maintain consistent vertical rhythm
        pdf.setStrokeColor(LIGHT_GRAY)
        pdf.line(LEFT_MARGIN, y, width - RIGHT_MARGIN, y)


    y -= 40
   
    qr_widget = qr.QrCodeWidget(order.invoice_number)
    qr_size = 70
    qr_drawing = Drawing(qr_size, qr_size)
    qr_drawing.add(qr_widget)
    renderPDF.draw(qr_drawing, pdf, LEFT_MARGIN, y - qr_size) 
    
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(LEFT_MARGIN + qr_size + 10, y - 10, "LOYALTY SUMMARY")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(LEFT_MARGIN + qr_size + 10, y - 22, f"Points Earned: {int(grand_total/10)}") #dummy
    pdf.setFillColor(ACCENT_BLUE)
    pdf.drawString(LEFT_MARGIN + qr_size + 10, y - 34, "Wishing you a speedy recovery!")

    calc_x = width - RIGHT_MARGIN
    pdf.setFillColor(black)
    pdf.setFont("Helvetica", 9)

    gst_rate = 0.12 
    total_base_amount = grand_total / (1 + gst_rate)
    total_gst_amount = grand_total - total_base_amount
    
    pdf.drawRightString(calc_x - 100, y - 10, "Subtotal (Taxable Value):")
    pdf.drawRightString(calc_x, y - 10, f"₹{total_base_amount:.2f}")
    
    pdf.drawRightString(calc_x - 100, y - 25, "CGST (6%):")
    pdf.drawRightString(calc_x, y - 25, f"₹{total_gst_amount/2:.2f}")
    
    pdf.drawRightString(calc_x - 100, y - 40, "SGST (6%):")
    pdf.drawRightString(calc_x, y - 40, f"₹{total_gst_amount/2:.2f}")

    pdf.setFillColor(ACCENT_BLUE)
    pdf.rect(width - 200, y - 70, 160, 26, fill=1, stroke=0) 
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 12) 
    pdf.drawRightString(width - RIGHT_MARGIN - 100, y - 62, "NET PAYABLE:") 
    pdf.drawRightString(width - RIGHT_MARGIN - 10, y - 62, f"₹{grand_total:.2f}") 


    pdf.setFillColor(black)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(LEFT_MARGIN, 100, "Terms & Conditions:")
    pdf.setFont("Helvetica", 7)
    pdf.setFillColor(TEXT_DIM)
    pdf.drawString(LEFT_MARGIN, 90, "• Warning: To be sold by retail on prescription of Registered Medical Practitioner (RMP) only.")
    pdf.drawString(LEFT_MARGIN, 82, "• Medicines once sold cannot be returned or exchanged.")
    pdf.drawString(LEFT_MARGIN, 74, "• Keep in a cool, dry place. Out of reach of children.")


    pdf.setFont("Helvetica-Bold", 8)
    pdf.setFillColor(TEXT_DIM)
    pdf.drawRightString(width - RIGHT_MARGIN, 85, "*** Computer Generated Invoice ***")
    pdf.drawRightString(width - RIGHT_MARGIN, 75, "No Signature Required")

    pdf.save()
    buffer.seek(0)
    return buffer
