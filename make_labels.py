"""Make labelled QR codes (QR + Equipment ID + Functional Location below).
pip install "qrcode[pil]" pandas openpyxl reportlab
Usage: python make_labels.py Switch_gear_FL.xlsx https://safe-isolation.vercel.app
Outputs: labels/<equipment>.png (one per equipment)  and  labels_sheet.pdf (A4, 3x4 per page)"""
import sys, os, io, pandas as pd, qrcode
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

src, base = sys.argv[1], sys.argv[2].rstrip("/")
df = pd.read_excel(src, dtype=str)
df["Equipment"] = df["Equipment"].str.strip()
df["Functional Location"] = df["Functional Location"].str.strip()
os.makedirs("labels", exist_ok=True)

def font(size, bold=False):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
              "C:/Windows/Fonts/%s.ttf" % ("arialbd" if bold else "arial"),
              "/Library/Fonts/Arial%s.ttf" % (" Bold" if bold else "")]:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def qr_img(eq):
    return qrcode.make(f"{base}/?e={eq}", box_size=10, border=2).convert("RGB")

def label_png(eq, fl):
    q = qr_img(eq); W = 520; pad = 20
    q = q.resize((W - 2*pad, W - 2*pad), Image.NEAREST)
    img = Image.new("RGB", (W, W + 110), "white"); d = ImageDraw.Draw(img)
    img.paste(q, (pad, pad))
    f1, f2 = font(34, True), font(26)
    for text, f, y in [(f"Equipment: {eq}", f1, W - 4), (fl, f2, W + 50)]:
        while d.textlength(text, font=f) > W - 20 and f.size > 12: f = font(f.size - 2, f is f1)
        d.text((W/2, y), text, font=f, fill="black", anchor="mt")
    d.rectangle([0, 0, W-1, W+109], outline="black", width=2)
    return img

# PNG per equipment
for eq, fl in zip(df["Equipment"], df["Functional Location"]):
    label_png(eq, fl).save(f"labels/{eq}.png")

# A4 PDF sheet, 3 x 4 labels per page
cols, rows = 3, 4
cw, ch = 60*mm, 66*mm
mx, my = (A4[0] - cols*cw) / 2, (A4[1] - rows*ch) / 2
c = canvas.Canvas("labels_sheet.pdf", pagesize=A4)
for i, (eq, fl) in enumerate(zip(df["Equipment"], df["Functional Location"])):
    k = i % (cols*rows)
    if i and k == 0: c.showPage()
    x = mx + (k % cols)*cw; y = A4[1] - my - (k // cols + 1)*ch
    c.setLineWidth(0.5); c.rect(x + 1*mm, y + 1*mm, cw - 2*mm, ch - 2*mm)
    c.drawImage(ImageReader(qr_img(eq)), x + 5*mm, y + 15*mm, 50*mm, 50*mm)
    c.setFont("Helvetica-Bold", 9.5); c.drawCentredString(x + cw/2, y + 10.5*mm, f"Equipment: {eq}")
    size = 8
    while c.stringWidth(fl, "Helvetica", size) > cw - 6*mm and size > 5: size -= 0.5
    c.setFont("Helvetica", size); c.drawCentredString(x + cw/2, y + 5*mm, fl)
c.save()
print(f"Done: {len(df)} labels in ./labels and labels_sheet.pdf")
