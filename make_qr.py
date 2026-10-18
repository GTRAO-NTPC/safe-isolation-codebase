"""Generate one QR PNG per equipment.  pip install qrcode[pil] pandas openpyxl
Usage: python make_qr.py Switch_gear_FL.xlsx https://your-site.example.com/"""
import sys, os, pandas as pd, qrcode
src, base = sys.argv[1], sys.argv[2].rstrip("/")
os.makedirs("qr", exist_ok=True)
for eq in pd.read_excel(src, dtype=str)["Equipment"].str.strip():
    qrcode.make(f"{base}/?e={eq}", box_size=8, border=2).save(f"qr/{eq}.png")
print("QR codes saved in ./qr")
