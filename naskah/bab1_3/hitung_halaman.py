"""Hitung nomor halaman setiap entri daftar dari PDF hasil render.
Pemakaian: python3 hitung_halaman.py DOKUMEN.pdf DOKUMEN.entries.json halaman.json"""
import json
import re
import subprocess
import sys

pdf, entries_f, out_f = sys.argv[1:4]
entries = json.load(open(entries_f))
n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
pages = [subprocess.run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), pdf, "-"], capture_output=True, text=True).stdout
         for i in range(1, n + 1)]


def norm(s):
    s = s.replace("­", "").replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


lines = [[norm(l) for l in p.splitlines() if norm(l)] for p in pages]
flat = [norm(p) for p in pages]
body_start = next(i for i, ls in enumerate(lines) if ls and ls[0] == "BAB I")


def roman(k):
    out = ""
    for v, r in [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]:
        while k >= v: out += r; k -= v
    return out


res, report = {}, []
cur = 0
for en in entries:
    if en.get("front"):
        pg = next(i for i in range(cur, body_start) if en["key"] in lines[i])
        disp = roman(pg + 1)
    else:
        lo = max(cur, body_start)
        if en["kind"] == "toc" and en["level"] == 0:
            pg = next(i for i in range(lo, n) if en["key"] in lines[i])
        else:
            key = norm(en["key"])
            pg = next((i for i in range(lo, n) if key in flat[i]), None)
            if pg is None:  # kunci mungkin terpotong pergantian halaman: pakai 25 karakter pertama
                pg = next(i for i in range(lo, n) if key[:25] in flat[i])
        disp = str(pg - body_start + 1)
    cur = pg
    res[en["bm"]] = disp
    report.append(f"{disp:>5}  {en['label']} {en['title'][:60]}")
json.dump(res, open(out_f, "w"), indent=1)
print(f"halaman PDF: {n}; halaman awal: {body_start}; badan: {n - body_start}")
print("\n".join(report))
