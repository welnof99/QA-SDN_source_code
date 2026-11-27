// Pustaka bersama untuk naskah BAB I-III (format sama dengan BAB VI: A4, TNR 12, spasi 1,5, margin 4-4-3-3 cm)
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, AlignmentType,
  WidthType, BorderStyle, ShadingType, LevelFormat, TabStopType, Footer, PageNumber,
  HeadingLevel, VerticalAlign, PageBreak,
} = require("docx");

const FONT = "Times New Roman";
const TEXTW = 11906 - 2268 - 1701;

function makeDoc(FIG, REFDB) {
  const body = [];
  let CH = "1";
  const order = [];            // kunci pustaka menurut urutan sitasi pertama
  function num(k) {
    if (!(k in REFDB)) throw new Error("Pustaka tidak dikenal: " + k);
    let i = order.indexOf(k); if (i < 0) { order.push(k); i = order.length - 1; } return i + 1;
  }
  function citeStr(keys) {     // gaya IEEE: [3], [5]–[7]
    const n = [...new Set(keys.map((k) => num(k.trim())))].sort((a, b) => a - b);
    const parts = []; let i = 0;
    while (i < n.length) { let j = i; while (j + 1 < n.length && n[j + 1] === n[j] + 1) j++;
      parts.push(j - i >= 2 ? `[${n[i]}]–[${n[j]}]` : n.slice(i, j + 1).map((x) => `[${x}]`).join(", ")); i = j + 1; }
    return parts.join(", ");
  }
  function runs(text, base = {}) {
    text = text.replace(/@\[([^\]]+)\]/g, (_, ks) => citeStr(ks.split(",")));
    const out = [];
    const re = /(\*\*[^*]+\*\*|\*[^*]+\*|_\{[^}]*\}|\^\{[^}]*\})/g;
    let last = 0, m;
    while ((m = re.exec(text)) !== null) {
      if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, ...base }));
      const t = m[0];
      if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, font: FONT, ...base }));
      else if (t.startsWith("_{")) out.push(new TextRun({ text: t.slice(2, -1), subScript: true, font: FONT, ...base }));
      else if (t.startsWith("^{")) out.push(new TextRun({ text: t.slice(2, -1), superScript: true, font: FONT, ...base }));
      else out.push(new TextRun({ text: t.slice(1, -1), italics: true, font: FONT, ...base }));
      last = m.index + t.length;
    }
    if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, ...base }));
    return out;
  }
  const P = (t, o = {}) => body.push(new Paragraph({
    children: runs(t), alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 567 },
    spacing: { line: 360, before: 0, after: 120 }, ...o }));
  const PN = (t) => P(t, { indent: { firstLine: 0 } });
  const H2 = (t) => body.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs(t) }));
  const H3 = (t) => body.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: runs(t) }));
  let listInst = 0;
  const LI = (t, ref, inst) => body.push(new Paragraph({
    numbering: { reference: ref, level: 0, instance: inst }, children: runs(t), alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 360, after: 60 } }));
  const OL = (items) => { listInst += 1; items.forEach((t) => LI(t, "angka", listInst)); };
  const UL = (items) => items.forEach((t) => LI(t, "titik", 0));

  let tabNo = 0;
  const border = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
  const borders = { top: border, bottom: border, left: border, right: border };
  function TABLE(title, header, rows, widthsCm, note, opt = {}) {
    tabNo += 1;
    const fs_ = opt.size || 20;
    body.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 200, after: 80, line: 276 },
      children: [new TextRun({ text: `Tabel ${CH}.${tabNo} `, bold: true, font: FONT }), ...runs(title)] }));
    const totalCm = widthsCm.reduce((a, b) => a + b, 0);
    const widths = widthsCm.map((w) => Math.round((w / totalCm) * TEXTW));
    widths[widths.length - 1] += TEXTW - widths.reduce((a, b) => a + b, 0);
    const cell = (t, i, head) => new TableCell({
      borders, width: { size: widths[i], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
      shading: head ? { fill: "E8E8E8", type: ShadingType.CLEAR, color: "auto" } : undefined,
      margins: { top: 50, bottom: 50, left: 90, right: 90 },
      children: [new Paragraph({ alignment: (i === 0 || opt.left) && !head ? AlignmentType.LEFT : AlignmentType.CENTER, spacing: { line: 240 },
        children: runs(t, { size: fs_, bold: head || undefined }) })] });
    body.push(new Table({
      width: { size: TEXTW, type: WidthType.DXA }, columnWidths: widths,
      rows: [new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, i, true)) }),
        ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, i, false)) }))] }));
    if (note) body.push(new Paragraph({ spacing: { before: 60, after: 200, line: 240 }, alignment: AlignmentType.JUSTIFIED,
      children: runs(note, { size: 20 }) }));
    else body.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
    return tabNo;
  }

  function pngSize(f) { const b = fs.readFileSync(f); return [b.readUInt32BE(16), b.readUInt32BE(20)]; }
  let figNo = 0;
  function FIGURE(file, caption, widthPx = 560) {
    figNo += 1;
    const f = path.join(FIG, file); const [w, h] = pngSize(f);
    body.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 160, after: 60 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(f), transformation: { width: widthPx, height: Math.round(widthPx * h / w) },
        altText: { title: `Gambar ${CH}.${figNo}`, description: caption, name: `Gambar ${CH}.${figNo}` } })] }));
    body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240, line: 276 },
      children: [new TextRun({ text: `Gambar ${CH}.${figNo} `, bold: true, font: FONT }), ...runs(caption)] }));
    return figNo;
  }

  let eqNo = 0;
  function EQ(file) {
    eqNo += 1;
    const f = path.join(FIG, "persamaan", file); const [w, h] = pngSize(f);
    let k = 96 / 300 * 0.85;
    const maxW = (TEXTW / 1440) * 96 - 70; // px, sisakan ruang untuk nomor
    if (w * k > maxW) k = maxW / w;
    body.push(new Paragraph({
      tabStops: [{ type: TabStopType.CENTER, position: Math.round(TEXTW / 2) }, { type: TabStopType.RIGHT, position: TEXTW - 20 }],
      spacing: { before: 120, after: 120 },
      children: [new TextRun({ text: "\t", font: FONT }),
        new ImageRun({ type: "png", data: fs.readFileSync(f), transformation: { width: Math.round(w * k), height: Math.round(h * k) },
          altText: { title: `Persamaan ${CH}.${eqNo}`, description: `Persamaan ${CH}.${eqNo}`, name: `Persamaan ${CH}.${eqNo}` } }),
        new TextRun({ text: `\t(${CH}.${eqNo})`, font: FONT })] }));
    return eqNo;
  }

  function TITLE(roman, title, ch, first = false) {
    CH = ch; tabNo = 0; figNo = 0; eqNo = 0;
    if (!first) body.push(new Paragraph({ children: [new PageBreak()] }));
    body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
      children: [new TextRun({ text: `BAB ${roman}`, bold: true, font: FONT, size: 28 })] }));
    body.push(new Paragraph({ heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: title, bold: true, font: FONT, size: 28 })] }));
  }

  function REFS() {
    body.push(new Paragraph({ children: [new PageBreak()] }));
    body.push(new Paragraph({ heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "DAFTAR PUSTAKA", bold: true, font: FONT, size: 28 })] }));
    order.forEach((k, i) => body.push(new Paragraph({ alignment: AlignmentType.LEFT,
      tabStops: [{ type: TabStopType.LEFT, position: 600 }], indent: { left: 600, hanging: 600 }, spacing: { line: 276, after: 140 },
      children: [new TextRun({ text: `[${i + 1}]\t`, font: FONT }), ...runs(REFDB[k])] })));
    const unused = Object.keys(REFDB).filter((k) => !order.includes(k));
    if (unused.length) console.log("Pustaka tidak dikutip:", unused.join(", "));
  }

  function save(OUT, title) {
    const doc = new Document({
      creator: "Welnof Satria", title, description: `Disertasi MAS-QA-SDN, ${title}`,
      styles: {
        default: { document: { run: { font: FONT, size: 24 } } },
        paragraphStyles: [
          { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
            run: { font: FONT, size: 28, bold: true }, paragraph: { spacing: { before: 0, after: 360, line: 360 }, keepNext: true, outlineLevel: 0, alignment: AlignmentType.CENTER } },
          { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
            run: { font: FONT, size: 24, bold: true }, paragraph: { spacing: { before: 240, after: 120, line: 360 }, keepNext: true, outlineLevel: 1 } },
          { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
            run: { font: FONT, size: 24, bold: true }, paragraph: { spacing: { before: 180, after: 100, line: 360 }, keepNext: true, outlineLevel: 2 } },
        ],
      },
      numbering: { config: [
        { reference: "angka", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 567, hanging: 340 } } } }] },
        { reference: "titik", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 567, hanging: 340 } } } }] },
      ] },
      sections: [{
        properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 2268, left: 2268, bottom: 1701, right: 1701 } } },
        footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 22 })] })] }) },
        children: body,
      }],
    });
    return Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log("ditulis", OUT, b.length, "byte; tabel", tabNo, "gambar", figNo, "persamaan", eqNo); });
  }
  const setChapter = (c) => { CH = c; tabNo = 0; figNo = 0; eqNo = 0; };
  return { setChapter, body, runs, P, PN, H2, H3, OL, UL, TABLE, FIGURE, EQ, TITLE, REFS, save, order };
}

module.exports = { makeDoc };
