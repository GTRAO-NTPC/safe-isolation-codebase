"""Rebuild index.html from the Excel file.  Usage: python build.py Switch_gear_FL.xlsx
Codes live in codes.csv. Existing codes are KEPT; only new equipment get new random codes."""
import sys, os, json, secrets, pandas as pd
src = sys.argv[1] if len(sys.argv) > 1 else "Switch_gear_FL.xlsx"
df = pd.read_excel(src, dtype=str).fillna("")
df["Equipment"] = df["Equipment"].str.strip()

# --- unique random 4-digit codes, persisted in codes.csv ---
codes = {}
if os.path.exists("codes.csv"):
    old = pd.read_csv("codes.csv", dtype=str)
    codes = dict(zip(old["Equipment"], old["Code"]))
used = set(codes.values())
free = [f"{n:04d}" for n in range(10000) if f"{n:04d}" not in used]
need = [e for e in df["Equipment"] if e not in codes]
if len(need) > len(free):
    sys.exit("Not enough free 4-digit codes")
for e in need:
    c = free.pop(secrets.randbelow(len(free)))
    codes[e] = c
print(f"{len(need)} new codes generated, {len(df)-len(need)} kept")

out = df[["Equipment", "Functional Location", "Object Description"]].copy()
out.insert(1, "Code", out["Equipment"].map(codes))
out.to_csv("codes.csv", index=False)

# --- build page ---
date = lambda s: s[:10]
data = {r["Equipment"]: {
    "c": codes[r["Equipment"]],
    "fl": r["Functional Location"].strip(), "d": r["Object Description"].strip(), "pl": r["Planning Plant"],
    }
    for _, r in df.iterrows()}
html = open("template.html", encoding="utf-8").read().replace(
    "/*DATA*/", json.dumps(data, separators=(",", ":"), ensure_ascii=False))
open("index.html", "w", encoding="utf-8").write(html)
print(f"index.html built: {len(data)} equipment, {len(html)/1024:.0f} KB")
