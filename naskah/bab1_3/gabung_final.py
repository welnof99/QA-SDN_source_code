"""Gabungkan Cover (halaman awal) dengan naskah BAB I-VII, lalu bangun Daftar Isi, Daftar Gambar, dan Daftar Tabel
dengan nomor halaman yang dihitung dari hasil render (dua lintasan) dan disimpan sebagai field PAGEREF.

Pemakaian:
  python3 gabung_final.py COVER.docx NASKAH_BAB_I-VII.docx KELUARAN.docx [halaman.json]
Tanpa halaman.json semua nomor diisi 0 (lintasan pertama). Dengan halaman.json nomor diisi dari hasil render.
Hasil juga menulis KELUARAN.entries.json (daftar entri + nama bookmark) untuk penghitungan halaman.
"""
import copy
import json
import re
import sys

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docxcompose.composer import Composer

cover_f, naskah_f, out_f = sys.argv[1:4]
PAGES = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else {}
FONT = "Times New Roman"
TEXTW = 11906 - 2268 - 1701

ABSTRAK = ("Penyeimbangan beban dan admisi flow pada *Software Defined Network* (SDN) pusat data merupakan masalah optimasi "
"kombinatorial: flow mana yang diterima dan melalui jalur mana, tanpa melampaui kapasitas tautan. Penelitian ini menilai secara "
"terkontrol peran *quantum annealing* untuk masalah tersebut dan mengembangkan arsitektur multi-agen MAS-QA-SDN dalam tiga tahap "
"pada topologi Fat-Tree. Tahap eksploratif merumuskan penempatan 100 flow ke 16 server sebagai QUBO 1.600 variabel; *Simulated "
"Quantum Annealing* (SQA) memberi *throughput* tertinggi (691,24 Mbps), sedangkan ACO memberi *latency* terendah serta GA memberi "
"*packet loss* dan indeks keadilan terbaik, sehingga tidak ada metode yang unggul pada semua metrik. Tahap terkontrol merumuskan "
"admisi flow dan pemilihan jalur pada 96 arc berarah sebagai QUBO enam suku dan membandingkan SQA dengan *Simulated Annealing* (SA) "
"dengan penyetelan pada seed validasi, anggaran setara, *repair* yang sama, dan uji berpasangan pada 30 seed. Dengan objektif "
"baseline, SQA kehilangan 1,6 dan 2,4 poin persentase (pp) flow lebih sedikit daripada SA pada 100 dan 150 flow, tetapi objektif "
"tersebut mencapai energi minimum ketika semua flow ditolak, dan keunggulan SQA hilang setelah reward admisi dikalibrasi. Langkah "
"*repair* merupakan faktor terbesar (tanpa *repair* 53–96% flow hilang), dekomposisi per pod mencapai hasil SQA monolitik dalam "
"0,6 pp dengan sekitar seperenam kerja *annealing*, dan pemrograman integer eksak masih 4,7–9,0 pp lebih baik. Tahap pengembangan "
"menunjukkan bahwa reward admisi analitis memberi kualitas setara dengan 40–49% kerja *annealing*, pentahapan prioritas menurunkan "
"kehilangan kelas EF menjadi 2–5% dengan biaya kenaikan kehilangan total 2,5–2,9 pp, sedangkan koordinasi harga antar-agen tidak "
"menambah kualitas di atas *repair* bersama pada Fat-Tree k = 4, 6, dan 8. Disimpulkan bahwa nilai MAS-QA terletak pada "
"dekomposisi yang murah dan dapat diparalelkan serta pada proteksi prioritas, bukan pada keunggulan pemecah kuantum. Seluruh "
"pemecah dijalankan sebagai simulasi klasik pada CPU, sehingga tidak ada klaim keunggulan perangkat keras kuantum.")
ABSTRACT = ("Load balancing and flow admission in data-centre Software Defined Networks (SDN) form a combinatorial optimization "
"problem: which flows to admit and on which paths, without exceeding link capacity. This research evaluates, under controlled "
"conditions, the role of quantum annealing for this problem and develops the multi-agent MAS-QA-SDN architecture in three stages "
"on a Fat-Tree topology. The exploratory stage formulates the placement of 100 flows on 16 servers as a 1,600-variable QUBO; "
"Simulated Quantum Annealing (SQA) gives the highest throughput (691.24 Mbps), while ACO gives the lowest latency and GA the best "
"packet loss and fairness index, so no method is best on every metric. The controlled stage formulates flow admission and path "
"selection on 96 directed arcs as a six-term QUBO and compares SQA with Simulated Annealing (SA) with tuning on validation seeds, "
"matched budgets, the same repair, and paired tests over 30 seeds. With the baseline objective, SQA loses 1.6 and 2.4 percentage "
"points (pp) fewer flows than SA at 100 and 150 flows, but this objective is minimized by rejecting all flows, and the SQA "
"advantage disappears once an admission reward is calibrated. Repair is the dominant factor (53–96% of flows are lost without "
"it), pod decomposition reaches monolithic SQA within 0.6 pp with about one-sixth of the annealing work, and exact integer "
"programming remains 4.7–9.0 pp better. The development stage shows that an analytic admission reward gives equal quality with "
"40–49% of the annealing work, priority staging reduces EF-class loss to 2–5% at a cost of 2.5–2.9 pp in total loss, and "
"price coordination between agents adds no quality over the shared repair on Fat-Tree k = 4, 6 and 8. The value of MAS-QA "
"therefore lies in cheap, parallelizable decomposition and priority protection, not in a quantum solver advantage. All solvers "
"run as classical simulations on a CPU, so no quantum hardware advantage is claimed.")


# ------------------------------------------------------------------ util XML
def el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn(k), str(v))
    return e


def run(text, bold=False, italic=False):
    r = el("w:r"); rpr = el("w:rPr")
    rpr.append(el("w:rFonts", **{"w:ascii": FONT, "w:hAnsi": FONT, "w:cs": FONT}))
    if bold: rpr.append(el("w:b"))
    if italic: rpr.append(el("w:i"))
    rpr.append(el("w:sz", **{"w:val": 24})); r.append(rpr)
    parts = text.split("\t")
    for i, part in enumerate(parts):
        if i: r.append(el("w:tab"))
        if part:
            t = el("w:t"); t.text = part; t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve"); r.append(t)
    return r


def md_runs(text, base_italic=False):
    out = []
    for i, seg in enumerate(re.split(r"\*", text)):
        if seg: out.append(run(seg, italic=(i % 2 == 1) != base_italic))
    return out


def set_para_runs(p, runs_):
    for r in list(p._p):
        if r.tag != qn("w:pPr"):
            p._p.remove(r)
    for r in runs_:
        p._p.append(r)


def ptext(p_el):
    return "".join(t.text or "" for t in p_el.iter(qn("w:t")))


def roman(n):
    vals = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    s = ""
    for v, r in vals:
        while n >= v: s += r; n -= v
    return s


# ------------------------------------------------------------------ 1. siapkan cover
cov = Document(cover_f)
for p in cov.paragraphs:
    for r in p.runs:
        if "Nertwork" in r.text or "NERTWORK" in r.text:
            r.text = r.text.replace("Nertwork", "Network").replace("NERTWORK", "NETWORK")
pars = cov.paragraphs
idx = {p.text.strip().rstrip("\t").strip(): i for i, p in enumerate(pars)}
i_abs = [i for i, p in enumerate(pars) if p.text.strip().startswith("ABSTRAK")][0]
i_abs_en = [i for i, p in enumerate(pars) if p.text.strip() == "ABSTRACT"][0]
set_para_runs(pars[i_abs + 1], md_runs(ABSTRAK))
set_para_runs(pars[i_abs_en + 1], md_runs(ABSTRACT, base_italic=True))
# hapus Daftar Isi/Gambar/Tabel lama
body = cov.element.body
i_toc = [i for i, p in enumerate(pars) if p.text.strip() == "DAFTAR ISI"][0]
start_el = pars[i_toc]._p
kids = list(body); k0 = kids.index(start_el)
for e in kids[k0:]:
    if e.tag != qn("w:sectPr"):
        body.remove(e)
# kunci spasi Normal cover (after 0, line 240) secara langsung agar tidak berubah oleh gaya naskah
for p in cov.element.body.iter(qn("w:p")):
    ppr = p.find(qn("w:pPr"))
    if ppr is None:
        ppr = el("w:pPr"); p.insert(0, ppr)
    sp = ppr.find(qn("w:spacing"))
    if sp is None:
        sp = el("w:spacing"); ppr.append(sp)
    if sp.get(qn("w:after")) is None: sp.set(qn("w:after"), "0")
    if sp.get(qn("w:line")) is None: sp.set(qn("w:line"), "240"); sp.set(qn("w:lineRule"), "auto")


def heading_para(text, page_break=True):
    p = el("w:p"); ppr = el("w:pPr")
    ppr.append(el("w:jc", **{"w:val": "center"}))
    ppr.append(el("w:spacing", **{"w:after": "360", "w:line": "240", "w:lineRule": "auto"}))
    p.append(ppr)
    if page_break:
        r = el("w:r"); r.append(el("w:br", **{"w:type": "page"})); p.append(r)
    p.append(run(text, bold=True))
    return p


def placeholder(tag):
    p = el("w:p"); p.append(run(tag)); return p


sect_final = body.find(qn("w:sectPr"))
for title, tag, pb in [("DAFTAR ISI", "@@TOC@@", False), ("DAFTAR GAMBAR", "@@LOF@@", True), ("DAFTAR TABEL", "@@LOT@@", True)]:
    h = heading_para(title, page_break=pb)
    if not pb:  # paragraf Keywords sudah membawa page break
        pass
    body.insert(list(body).index(sect_final), h)
    body.insert(list(body).index(sect_final), placeholder(tag))

# ------------------------------------------------------------------ 2. gabungkan
master = Document(naskah_f)
comp = Composer(master)
comp.insert(0, cov)
doc = comp.doc
body = doc.element.body

# section break di akhir halaman awal: romawi kecil, halaman sampul tanpa nomor
first_bab = [e for e in body if e.tag == qn("w:p") and ptext(e).strip() == "BAB I"][0]
final_sect = body.find(qn("w:sectPr"))
fm_sect = copy.deepcopy(final_sect)
for t in fm_sect.findall(qn("w:pgNumType")): fm_sect.remove(t)
for t in fm_sect.findall(qn("w:titlePg")): fm_sect.remove(t)
pg = el("w:pgNumType", **{"w:fmt": "lowerRoman", "w:start": "1"})
# urutan elemen sectPr: footerReference, ..., pgSz, pgMar, ..., pgNumType, cols, ..., titlePg, ..., docGrid
pgmar = fm_sect.find(qn("w:pgMar"))
pgmar.addnext(pg)
grid = fm_sect.find(qn("w:docGrid"))
tp = el("w:titlePg")
if grid is not None: grid.addprevious(tp)
else: fm_sect.append(tp)
sb = el("w:p"); sbp = el("w:pPr"); sbp.append(fm_sect); sb.append(sbp)
first_bab.addprevious(sb)
for t in final_sect.findall(qn("w:pgNumType")): final_sect.remove(t)
for t in final_sect.findall(qn("w:titlePg")): final_sect.remove(t)
final_sect.find(qn("w:pgMar")).addnext(el("w:pgNumType", **{"w:fmt": "decimal", "w:start": "1"}))

# ------------------------------------------------------------------ 3. kumpulkan entri dan pasang bookmark
bm_id = [9000]


def bookmark(p_el, name):
    s = el("w:bookmarkStart", **{"w:id": bm_id[0], "w:name": name}); e = el("w:bookmarkEnd", **{"w:id": bm_id[0]})
    bm_id[0] += 1
    ppr = p_el.find(qn("w:pPr"))
    if ppr is not None: ppr.addnext(s)
    else: p_el.insert(0, s)
    p_el.append(e)


def is_bold_para(p_el):
    rs = [r for r in p_el.iter(qn("w:r")) if "".join(t.text or "" for t in r.iter(qn("w:t"))).strip()]
    if not rs: return False
    pstyle = p_el.find(qn("w:pPr") + "/" + qn("w:pStyle"))
    if pstyle is not None and pstyle.get(qn("w:val")).startswith("Heading"): return True
    def b(r):
        rpr = r.find(qn("w:rPr")); bb = rpr.find(qn("w:b")) if rpr is not None else None
        return bb is not None and bb.get(qn("w:val")) not in ("0", "false")
    return all(b(r) for r in rs)


def has_drawing(e):
    return e.find(".//" + qn("w:drawing")) is not None


ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7}
entries = []
front_titles = ["LEMBAR PENGESAHAN", "LEMBARAN PENGESAHAN KOMISI PENGUJI", "KATA PENGANTAR", "ABSTRAK", "ABSTRACT",
                "DAFTAR ISI", "DAFTAR GAMBAR", "DAFTAR TABEL"]
top = list(body)
sb_index = top.index(sb)
seen_front = set()
for e in top[:sb_index]:
    if e.tag != qn("w:p"): continue
    t = ptext(e).strip().rstrip("\t").strip()
    if t in front_titles and t not in seen_front:
        seen_front.add(t); name = f"dis_fm_{len(entries):03d}"; bookmark(e, name)
        entries.append({"kind": "toc", "level": 0, "label": t, "title": "", "bm": name, "front": True, "key": t})

chap = 0; v_auto = 0; prev_text = ""
body_items = top[sb_index + 1:]
for j, e in enumerate(body_items):
    if e.tag != qn("w:p"):
        continue
    t = re.sub(r"\s+", " ", ptext(e)).strip()
    if not t:
        continue
    m = re.fullmatch(r"BAB (I|II|III|IV|V|VI|VII)", t)
    if m:
        chap = ROMAN[m.group(1)]
        k = j + 1
        while ptext(body_items[k]).strip() == "": k += 1
        title = re.sub(r"\s+", " ", ptext(body_items[k])).strip()
        name = f"dis_bab_{chap}"; bookmark(e, name)
        entries.append({"kind": "toc", "level": 0, "label": f"BAB {m.group(1)}", "title": title, "bm": name, "key": f"BAB {m.group(1)}"})
        continue
    if t == "DAFTAR PUSTAKA":
        bookmark(e, "dis_pustaka")
        entries.append({"kind": "toc", "level": 0, "label": "DAFTAR PUSTAKA", "title": "", "bm": "dis_pustaka", "key": "DAFTAR PUSTAKA"})
        continue
    m = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?\s+(\S.*)$", t)
    if m and int(m.group(1)) == chap and len(t) < 160 and is_bold_para(e) and not t.endswith("."):
        if not re.match(r"^\d+\.\d+\.\d+\.\d+", t):
            lvl = 2 if m.group(3) else 1
            num = ".".join(x for x in m.group(1, 2, 3) if x)
            name = f"dis_h_{len(entries):03d}"; bookmark(e, name)
            entries.append({"kind": "toc", "level": lvl, "label": num, "title": m.group(4), "bm": name, "key": t[:60]})
        continue
    # subbab BAB V yang bernomor otomatis (5.3.1-5.3.7)
    numpr = e.find(qn("w:pPr") + "/" + qn("w:numPr"))
    if chap == 5 and numpr is not None and is_bold_para(e) and len(t) < 120:
        v_auto += 1
        num = f"5.3.{v_auto}"; name = f"dis_h_{len(entries):03d}"; bookmark(e, name)
        entries.append({"kind": "toc", "level": 2, "label": num, "title": t, "bm": name, "key": t[:50]})
        continue
    # keterangan gambar: diawali "Gambar N.M" dan berada sesudah paragraf bergambar
    m = re.match(r"^Gambar (\d+)\.(\d+)\s+(\S.*)$", t)
    if m and m.group(3)[0].islower():
        continue
    if m:
        prev = [x for x in body_items[max(0, j - 3):j] if x.tag == qn("w:p")]
        if any(has_drawing(x) for x in prev) or has_drawing(e):
            name = f"dis_g_{len(entries):03d}"; bookmark(e, name)
            entries.append({"kind": "lof", "level": 0, "label": f"Gambar {m.group(1)}.{m.group(2)}", "title": m.group(3).rstrip("."), "bm": name, "key": t[:45]})
        continue
    # judul tabel: diawali "Tabel N.M" dan diikuti tabel dalam 2 elemen
    m = re.match(r"^Tabel (\d+)\.(\d+)\s+(\S.*)$", t)
    if m and m.group(3)[0].islower():
        continue
    if m:
        nxt = body_items[j + 1:j + 3]
        if any(x.tag == qn("w:tbl") for x in nxt):
            name = f"dis_t_{len(entries):03d}"; bookmark(e, name)
            entries.append({"kind": "lot", "level": 0, "label": f"Tabel {m.group(1)}.{m.group(2)}", "title": m.group(3).rstrip("."), "bm": name, "key": t[:45]})
        continue

# ------------------------------------------------------------------ 4. bangun paragraf daftar
def first_sentence(t):
    m = re.search(r"\.\s+(?=[A-Z])", t)
    return t[:m.start()] if m and m.start() > 20 else t


def entry_para(en):
    p = el("w:p"); ppr = el("w:pPr")
    tabs = el("w:tabs"); tabs.append(el("w:tab", **{"w:val": "right", "w:leader": "dot", "w:pos": TEXTW})); ppr.append(tabs)
    ppr.append(el("w:spacing", **{"w:before": "0", "w:after": "80", "w:line": "276", "w:lineRule": "auto"}))
    if en["kind"] == "toc":
        left, hang = {0: (851, 851), 1: (1134, 567), 2: (1985, 851)}[en["level"]]
        if en["level"] == 0 and (en.get("front") or en["label"] == "DAFTAR PUSTAKA"):
            left, hang = 0, 0
    else:
        left, hang = 1418, 1418
    ppr.append(el("w:ind", **{"w:left": left, "w:hanging": hang, "w:right": 567}))
    ppr.append(el("w:jc", **{"w:val": "left"}))
    p.append(ppr)
    if en["kind"] == "toc" and en["level"] == 0:
        txt = en["label"] + (" " + en["title"] if en["title"] else "")
        p.append(run(txt, bold=True))
    elif en["kind"] == "toc":
        p.append(run(en["label"] + "\t")); p.extend(md_runs(en["title"]))
    else:
        p.append(run(en["label"], bold=True)); p.append(run("\t")); p.extend(md_runs(first_sentence(en["title"])))
    p.append(run("\t"))
    cached = str(PAGES.get(en["bm"], "0"))
    if en.get("front"):  # halaman awal: teks tetap (romawi) agar tampil benar di semua aplikasi
        p.append(run(cached, bold=True))
        return p
    r1 = el("w:r"); r1.append(el("w:fldChar", **{"w:fldCharType": "begin"})); p.append(r1)
    r2 = el("w:r"); it = el("w:instrText"); it.text = f" PAGEREF {en['bm']} \\h "
    it.set("{http://www.w3.org/XML/1998/namespace}space", "preserve"); r2.append(it); p.append(r2)
    r3 = el("w:r"); r3.append(el("w:fldChar", **{"w:fldCharType": "separate"})); p.append(r3)
    p.append(run(cached, bold=(en["kind"] == "toc" and en["level"] == 0)))
    r5 = el("w:r"); r5.append(el("w:fldChar", **{"w:fldCharType": "end"})); p.append(r5)
    return p


for tag, kind in [("@@TOC@@", "toc"), ("@@LOF@@", "lof"), ("@@LOT@@", "lot")]:
    ph = [e for e in body if e.tag == qn("w:p") and ptext(e).strip() == tag][0]
    for en in [x for x in entries if x["kind"] == kind]:
        ph.addprevious(entry_para(en))
    body.remove(ph)

# minta Word memperbarui field (PAGEREF) saat dokumen dibuka
settings = doc.settings.element
if settings.find(qn("w:updateFields")) is None:
    settings.append(el("w:updateFields", **{"w:val": "true"}))

doc.save(out_f)
json.dump(entries, open(out_f.replace(".docx", ".entries.json"), "w"), ensure_ascii=False, indent=1)
print("entri: toc", sum(e["kind"] == "toc" for e in entries), "gambar", sum(e["kind"] == "lof" for e in entries),
      "tabel", sum(e["kind"] == "lot" for e in entries))
