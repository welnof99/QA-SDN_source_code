"""Gabungkan BAB I-III (dibangun ulang), BAB IV, V, VI (berkas Anda), dan BAB VII + Daftar Pustaka menjadi satu .docx.
- Sitasi nama-tahun di BAB V dan VI diganti nomor IEEE sesuai urutan pada BAB I-III.
- Daftar pustaka per bab di BAB V dan VI dihapus; satu Daftar Pustaka gabungan di akhir.
- Gambar yang lebih lebar dari bidang teks (margin 4-3 cm) diperkecil proporsional.
Pemakaian: python3 gabung_disertasi.py PART_I-III.docx ORDER.json BAB_IV.docx BAB_V.docx BAB_VI.docx PART_VII.docx KELUARAN.docx
"""
import json
import re
import sys
import unicodedata
from copy import deepcopy

from docx import Document
from docx.enum.text import WD_BREAK
from docx.oxml.ns import qn
from docxcompose.composer import Composer

part13, order_json, f4, f5, f6, part7, out = sys.argv[1:8]
ORDER = json.load(open(order_json))
NUM = {k: i + 1 for i, k in enumerate(ORDER)}


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()


def key_of(author, year):
    sur = fold(author.strip().split()[0].split("-")[0])
    k = f"{sur}{year}"
    if k not in NUM:
        raise KeyError(f"Sitasi tidak dikenal: {author} {year} -> {k}")
    return k


def cite_str(nums):
    n = sorted(set(nums)); parts = []; i = 0
    while i < len(n):
        j = i
        while j + 1 < len(n) and n[j + 1] == n[j] + 1:
            j += 1
        parts.append(f"[{n[i]}]–[{n[j]}]" if j - i >= 2 else ", ".join(f"[{x}]" for x in n[i:j + 1]))
        i = j + 1
    return ", ".join(parts)


YEAR = r"(?:19|20)\d{2}"
PAREN = re.compile(r"\((?:[A-ZŞ][^()]*?, " + YEAR + r")(?:; [A-ZŞ][^()]*?, " + YEAR + r")*\)")
NARR = re.compile(r"([A-ZŞ][\w\-ñ]+(?: dkk\.| et al\.| dan [A-Z]\w+| & [A-Z]\w+)?) \((" + YEAR + r")\)")


def paren_rep(m):
    inner = m.group(0)[1:-1]
    nums = []
    for part in inner.split(";"):
        a, y = part.rsplit(",", 1)
        nums.append(NUM[key_of(a, y.strip())])
    return cite_str(nums)


def narr_rep(m):
    return f"{m.group(1)} {cite_str([NUM[key_of(m.group(1), m.group(2))]])}"


def replace_runs(p, pattern, func):
    count = 0
    while True:
        runs = p.runs
        text = "".join(r.text for r in runs)
        m = pattern.search(text)
        if not m:
            return count
        s, e = m.span(); rep = func(m); pos = 0; done = False
        for r in runs:
            rs, re_ = pos, pos + len(r.text); pos = re_
            if re_ <= s or rs >= e:
                continue
            if not done:
                r.text = r.text[: s - rs] + rep + (r.text[e - rs:] if e <= re_ else "")
                done = True
            else:
                r.text = r.text[e - rs:] if e < re_ else ""
        count += 1


def convert(doc):
    n = 0
    for p in doc.paragraphs:
        n += replace_runs(p, PAREN, paren_rep)
        n += replace_runs(p, NARR, narr_rep)
    for t in doc.tables:
        for row in t.rows:
            for c in row.cells:
                for p in c.paragraphs:
                    n += replace_runs(p, PAREN, paren_rep) + replace_runs(p, NARR, narr_rep)
    return n


def drop_reference_section(doc):
    body = doc.element.body
    kids = list(body)
    start = None
    for i, el in enumerate(kids):
        if el.tag == qn("w:p"):
            txt = "".join(t.text or "" for t in el.iter(qn("w:t"))).strip()
            if txt.upper() == "DAFTAR PUSTAKA":
                start = i
    if start is None:
        return 0
    removed = 0
    for el in kids[start:]:
        if el.tag != qn("w:sectPr"):
            body.remove(el); removed += 1
    return removed


docs = {}
for name, f in [("IV", f4), ("V", f5), ("VI", f6)]:
    d = Document(f)
    c = convert(d) if name in ("V", "VI") else 0
    r = drop_reference_section(d) if name in ("V", "VI") else 0
    print(f"BAB {name}: {c} sitasi diganti, {r} elemen daftar pustaka bab dihapus")
    docs[name] = d

master = Document(part13)
# samakan spasi-setelah Normal dengan BAB V (6 pt) agar paragraf BAB IV-V tidak menempel
from docx.shared import Pt
master.styles['Normal'].paragraph_format.space_after = Pt(6)
comp = Composer(master)
for name in ("IV", "V", "VI"):
    comp.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    comp.append(docs[name])
comp.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
comp.append(Document(part7))

# perkecil gambar yang melebihi bidang teks
sec = comp.doc.sections[-1]
textw = sec.page_width - sec.left_margin - sec.right_margin
scaled = 0
for shp in comp.doc.inline_shapes:
    if shp.width > textw:
        k = textw / shp.width
        shp.height = int(shp.height * k); shp.width = int(textw); scaled += 1
print("gambar diperkecil:", scaled)
comp.save(out)
print("ditulis", out)
