const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, AlignmentType,
  WidthType, BorderStyle, ShadingType, LevelFormat, TabStopType, Footer, PageNumber,
  HeadingLevel, VerticalAlign,
} = require("docx");

const FIG = require("path").join(__dirname, "..", "figures", "chapter6");
const OUT = process.argv[2] || "BAB_VI.docx";
const FONT = "Times New Roman";
const TEXTW = 11906 - 2268 - 1701; // A4 - kiri 4 cm - kanan 3 cm (DXA)

// ---------- markup sederhana: **tebal**, *miring*, _{subskrip}, ^{superskrip}
function runs(text, base = {}) {
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

const body = [];
const P = (t, o = {}) => body.push(new Paragraph({
  children: runs(t), alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 567 },
  spacing: { line: 360, before: 0, after: 120 }, ...o }));
const PN = (t) => P(t, { indent: { firstLine: 0 } });
const H2 = (t) => body.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs(t) }));
const H3 = (t) => body.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: runs(t) }));
const LI = (t, ref = "angka", level = 0, inst = 0) => body.push(new Paragraph({
  numbering: { reference: ref, level, instance: inst }, children: runs(t), alignment: AlignmentType.JUSTIFIED,
  spacing: { line: 360, after: 60 } }));
let listInst = 0;
const OL = (items) => { listInst += 1; items.forEach((t) => LI(t, "angka", 0, listInst)); };
const UL = (items) => items.forEach((t) => LI(t, "titik", 0, 0));

// ---------- tabel
let tabNo = 0;
const border = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const borders = { top: border, bottom: border, left: border, right: border };
function TABLE(title, header, rows, widthsCm, note) {
  tabNo += 1;
  body.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 200, after: 80, line: 276 },
    children: [new TextRun({ text: `Tabel 6.${tabNo} `, bold: true, font: FONT }), ...runs(title)] }));
  const totalCm = widthsCm.reduce((a, b) => a + b, 0);
  const widths = widthsCm.map((w) => Math.round((w / totalCm) * TEXTW));
  widths[widths.length - 1] += TEXTW - widths.reduce((a, b) => a + b, 0);
  const cell = (t, i, head) => new TableCell({
    borders, width: { size: widths[i], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
    shading: head ? { fill: "E8E8E8", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: [new Paragraph({ alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER, spacing: { line: 240 },
      children: runs(t, { size: 20, bold: head || undefined }) })] });
  body.push(new Table({
    width: { size: TEXTW, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, i, true)) }),
      ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, i, false)) }))] }));
  if (note) body.push(new Paragraph({ spacing: { before: 60, after: 200, line: 240 }, alignment: AlignmentType.JUSTIFIED,
    children: runs(note, { size: 20 }) }));
  else body.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
  return tabNo;
}

// ---------- gambar
function pngSize(f) { const b = fs.readFileSync(f); return [b.readUInt32BE(16), b.readUInt32BE(20)]; }
let figNo = 0;
function FIGURE(file, caption, widthPx = 520) {
  figNo += 1;
  const f = path.join(FIG, file); const [w, h] = pngSize(f);
  body.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 160, after: 60 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(f), transformation: { width: widthPx, height: Math.round(widthPx * h / w) },
      altText: { title: `Gambar 6.${figNo}`, description: caption, name: `Gambar 6.${figNo}` } })] }));
  body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240, line: 276 },
    children: [new TextRun({ text: `Gambar 6.${figNo} `, bold: true, font: FONT }), ...runs(caption)] }));
  return figNo;
}

// ---------- persamaan
let eqNo = 0;
function EQ(file) {
  eqNo += 1;
  const f = path.join(FIG, "persamaan", file); const [w, h] = pngSize(f);
  const k = 96 / 300 * 0.85;
  body.push(new Paragraph({
    tabStops: [{ type: TabStopType.CENTER, position: Math.round(TEXTW / 2) }, { type: TabStopType.RIGHT, position: TEXTW - 20 }],
    spacing: { before: 120, after: 120 },
    children: [new TextRun({ text: "\t", font: FONT }),
      new ImageRun({ type: "png", data: fs.readFileSync(f), transformation: { width: Math.round(w * k), height: Math.round(h * k) },
        altText: { title: `Persamaan 6.${eqNo}`, description: `Persamaan 6.${eqNo}`, name: `Persamaan 6.${eqNo}` } }),
      new TextRun({ text: `\t(6.${eqNo})`, font: FONT })] }));
  return eqNo;
}

// =====================================================================  ISI
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
  children: [new TextRun({ text: "BAB VI", bold: true, font: FONT, size: 28 })] }));
body.push(new Paragraph({ heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: "ADMISI FLOW MULTI-AGEN BERBASIS QUANTUM ANNEALING PADA SDN: REWARD ADMISI ANALITIS, PROTEKSI PRIORITAS, DAN BATAS KOORDINASI HARGA", bold: true, font: FONT, size: 28 })] }));

H2("6.1 Pendahuluan");
P("Bab ini melanjutkan pipeline MAS-QA multi-agen dari bab sebelumnya, yaitu dekomposisi masalah admisi flow menjadi satu agen per pod sumber yang masing-masing menyelesaikan QUBO lokal dengan *simulated quantum annealing* (SQA) (Yarkoni dkk., 2022), diikuti satu tahap *repair* bersama yang menjamin kelayakan kapasitas. Bab sebelumnya menunjukkan bahwa keunggulan SQA atas *simulated annealing* (SA) bergantung pada fungsi objektif dan aturan *repair*, bukan pada solver itu sendiri. Temuan tersebut tidak mengakhiri penelitian, tetapi menunjukkan bagian mana dari pipeline yang perlu diperbaiki.");
P("Tiga perbaikan dirancang dan diuji dalam bab ini: reward admisi analitis yang menghilangkan bias \"tolak semua\" pada objektif, pentahapan prioritas yang melindungi kelas *Expedited Forwarding* (EF), dan koordinasi harga antar-agen pada arc yang dipakai bersama. Dua perbaikan pertama terbukti bermanfaat, sedangkan koordinasi harga tidak menambah kualitas di atas *repair* bersama pada Fat-Tree k = 4, 6 maupun 8. Temuan negatif ini dilaporkan secara terkontrol karena menjelaskan batas peran koordinasi dalam arsitektur multi-agen.");
P("Penyeimbangan beban dan rekayasa trafik pada SDN telah dikaji luas, mulai dari heuristik berbasis aliran hingga pembelajaran penguatan dan sistem multi-agen (Hamdan dkk., 2021; Xia dkk., 2022; Bhavanasi dkk., 2023; Ye dkk., 2023). Di sisi lain, formulasi QUBO dan *quantum annealing* telah diterapkan pada optimasi lalu lintas, perutean jaringan sensor nirkabel, penempatan fungsi jaringan virtual, pemanfaatan bandwidth, serta alokasi sumber daya jaringan optik (Inoue dkk., 2021; Chen dkk., 2022; Chiavassa dkk., 2022; Tsai dkk., 2023; Şeker dkk., 2024; Witt dkk., 2024). Berbagai mesin Ising, baik kuantum maupun klasik, juga dikembangkan sebagai pemecah QUBO (Mohseni dkk., 2022). Bab ini berada di persimpangan kedua arus tersebut, dengan penekanan pada evaluasi yang terkontrol.");

H3("6.1.1 Posisi Bab terhadap Temuan Sebelumnya");
P("Tabel 6.1 merangkum enam temuan bab sebelumnya yang menjadi titik tolak bab ini, beserta subbab yang menjawabnya.");
TABLE("Temuan bab sebelumnya dan subbab yang menjawabnya", ["Temuan bab sebelumnya", "Implikasi", "Dijawab pada"], [
  ["Objektif baseline mencapai energi minimum saat semua flow ditolak", "Solver tidak mengoptimalkan admisi; hasil ditentukan oleh *repair*", "6.2, 6.6.1"],
  ["*Repair* menyumbang porsi terbesar hasil akhir; solver hanya menambah 3,5–8,4 pp di atas greedy", "Kontribusi solver perlu diperbesar melalui objektif dan koordinasi", "6.2, 6.3"],
  ["Dekomposisi per pod memakai sekitar 1/6 kerja annealing, tetapi pod tidak saling melihat beban (b_{l} = 0)", "Kapasitas arc bersama baru ditegakkan setelah solver", "6.3, 6.6.3"],
  ["Varian iteratif (ITER-SQA-v2-R3) tidak memberi perbaikan signifikan dan tidak konvergen", "Diperlukan mekanisme koordinasi dengan dasar konvergensi", "6.3, 6.6.3"],
  ["Kehilangan flow kelas EF tinggi (34–53% pada 100–150 flow)", "Urutan prioritas pada *repair* tidak cukup melindungi kelas utama", "6.4, 6.6.2"],
  ["IP eksak menerima 4,7–9,0 pp lebih banyak flow pada k = 4", "Manfaat praktis annealing perlu diuji pada ukuran lebih besar", "6.6.5"],
], [6.2, 5.6, 2.2]);

H3("6.1.2 Pertanyaan Penelitian");
P("Bab ini menjawab lima pertanyaan penelitian berikut.");
OL([
  "**RQ6.1** — Apakah reward admisi μ_{f} yang diturunkan secara analitis menghilangkan bias \"tolak semua\" tanpa pemilihan μ secara empiris, dan dengan biaya komputasi berapa?",
  "**RQ6.2** — Apakah penyelesaian bertahap per kelas (EF, AF, BE) menurunkan kehilangan EF, dan berapa biayanya terhadap PL_{flow} total?",
  "**RQ6.3** — Apakah koordinasi harga antar-agen pod menambah kualitas di atas *repair* bersama, setelah efek derau sampler dan pemilihan sampel terbaik dikontrol?",
  "**RQ6.4** — Bagaimana alokasi anggaran annealing (banyak sampel pendek dibanding sedikit sampel panjang) memengaruhi kehilangan flow pada kerja yang setara?",
  "**RQ6.5** — Pada ukuran Fat-Tree berapa pipeline multi-agen mulai lebih praktis daripada pemrograman integer eksak, ditinjau dari kualitas dan waktu penyelesaian?",
]);

H3("6.1.3 Kontribusi Bab");
UL([
  "Syarat analitis reward admisi μ_{f} per flow, yang memberi kualitas setara MAS-QA-v2 dengan 40–49% kerja annealing karena slack biner pada arc bersama dapat dihapus dari QUBO pod.",
  "Pentahapan prioritas leksikografis yang menurunkan kehilangan EF dari 18–56% menjadi 2–5%, dengan biaya kenaikan PL_{flow} total 2,5–2,9 pp pada beban tinggi.",
  "Evaluasi terkontrol koordinasi harga antar-agen pada k = 4, 6 dan 8, termasuk kontrol derau sampler dan kontrol \"terbaik dari K restart\", yang menunjukkan bahwa *repair* bersama sudah berfungsi sebagai koordinator implisit.",
  "Temuan alokasi anggaran: pada k = 4, membagi kerja yang sama menjadi delapan sampel pendek menurunkan PL_{flow} 1,1–2,9 pp, tetapi efek ini hilang pada k = 6.",
  "Perbandingan berprotokol setara dengan pemrograman integer eksak, yang menunjukkan bahwa titik silang kualitas belum tercapai pada ukuran yang diuji.",
]);

H3("6.1.4 Batasan");
P("Semua solver dijalankan sebagai simulasi klasik pada CPU, sehingga bab ini tidak mengklaim keunggulan perangkat keras kuantum. Protokol evaluasi (seed validasi dan evaluasi yang terpisah, penyetaraan anggaran, *repair* yang sama, dan uji berpasangan) dipertahankan sama dengan bab sebelumnya agar hasil antarbab dapat dibandingkan langsung. Seluruh eksperimen dirancang agar dapat dijalankan pada komputer dua core dalam sekitar satu jam.");

// ------------------------------------------------------------------ 6.2
H2("6.2 Reward Admisi Analitis");
P("Subbab ini menurunkan besar reward admisi μ_{f} per flow yang cukup untuk membuat penerimaan flow yang layak menurunkan energi QUBO. Hasilnya menggantikan pemilihan μ = 20 secara empiris pada bab sebelumnya dengan aturan yang dapat dihitung sebelum solver dijalankan.");
H3("6.2.1 Akar Masalah");
P("Pada bobot baseline λ = (10, 10, 5, 3, 2, 1), suku *balance* mendominasi. Untuk flow 23,6 Mbps pada jalur enam arc, H_{bal} naik sekitar 1,25 sehingga energi naik sekitar 6,3, sedangkan reward bandwidth hanya sekitar 0,04. Akibatnya keadaan \"semua ditolak\" menjadi minimum global, sebagaimana dibuktikan dengan enumerasi lengkap pada bab sebelumnya.");
H3("6.2.2 Perubahan Energi Akibat Menerima Satu Flow");
P("Misalkan flow f diterima pada jalur p yang berisi h arc dan masih memiliki kapasitas sisa, dengan a_{f} = d_{f}/c sebagai pertambahan utilisasi pada setiap arc di p. Karena y_{f} = 1 dan x_{f,p} = 1, suku *one-hot* tidak berubah. Perubahan energinya adalah:");
EQ("pers6_1.png");
P("Suku *balance* dapat diuraikan secara tertutup, dengan ū sebagai utilisasi rata-rata seluruh |E| arc:", { indent: { firstLine: 0 } });
EQ("pers6_2.png");
P("Untuk jaringan kosong, a_{f} = 0,472 dan h = 6 memberi ΔH_{bal} ≈ 1,25, sama dengan nilai yang dilaporkan pada bab sebelumnya. Untuk suku *fairness*, dengan δ_{k} = d_{f}/D_{k} pada kelas k dan dua kelas lain sebagai pasangan, batas atasnya adalah ΔH_{fair} ≤ 2(2δ_{k} + δ_{k}^{2}). Galat kuantisasi slack berukuran ε_{cap} ≤ h/(4(2^{K} − 1)^{2}), sekitar 3,8 × 10^{−4} untuk K = 6 dan h = 6, sehingga dapat diabaikan.");
H3("6.2.3 Syarat Reward Admisi");
P("Menerima flow f menurunkan energi apabila ΔE_{f} < 0 pada setidaknya satu jalur kandidat. Reward minimum yang cukup adalah:");
EQ("pers6_3.png");
P("Reward yang dipakai ditambah margin kecil ε = 0,1 dan ditambahkan ke diagonal variabel y_{f}:", { indent: { firstLine: 0 } });
EQ("pers6_4.png");
P("Dua cara mengisi u_{l} dibandingkan. Batas kasus terburuk (u_{l} = 1, ū = 0) berlaku untuk semua keadaan, tetapi sangat besar: pada satu instans S2, nilainya berkisar 5,0–116,4 dengan median 15,7. Batas berbasis beban memakai beban yang diketahui; untuk jaringan kosong nilainya berkisar 1,6–44,3 dengan median 4,1. Varian berbasis beban dipakai di seluruh bab ini. Pada evaluasi akhir, yang menjalankan agen pod satu putaran, beban latar bernilai nol sehingga μ_{f} adalah batas untuk jaringan kosong. Pendekatan ini menggantikan satu nilai μ global dengan reward yang berbeda untuk setiap flow sesuai ukuran dan jalurnya.");
H3("6.2.4 Konsekuensi terhadap Struktur QUBO Pod");
P("Karena kapasitas arc bersama ditegakkan oleh *repair* (atau oleh harga pada Subbab 6.3), slack biner untuk arc bersama dapat dihapus dari QUBO pod. Slack hanya dipertahankan untuk arc lokal. Penghapusan ini menjadi sumber utama penghematan kerja annealing yang dilaporkan pada Subbab 6.6.1.");
P("Penalti kapasitas berbentuk kuadratik, λ_{c}(e/c)^{2} untuk kelebihan beban e, sehingga kelebihan kecil hampir tidak dihukum. Syarat λ_{c}(e/c)^{2} > μ_{f} hanya dapat dijamin untuk pelanggaran yang cukup besar, sedangkan pelanggaran kecil tetap diserahkan ke *repair*. Pemilihan bobot penalti merupakan masalah umum pada formulasi QUBO berkendala (Glover dkk., 2022; Verma dan Lewis, 2022). Pendekatan *unbalanced penalization*, yang mengodekan kendala pertidaksamaan tanpa slack biner (Montañez-Barrera dkk., 2024), merupakan alternatif yang belum diuji dalam bab ini.");

// ------------------------------------------------------------------ 6.3
H2("6.3 Arsitektur Multi-Agen dan Koordinasi Harga");
P("Setiap pod diperlakukan sebagai agen yang menyelesaikan QUBO lokalnya sendiri. Keputusan semua agen kemudian digabungkan oleh *repair* bersama, yang berperan sebagai koordinator global (Gambar 6.1). Pada studi pendahuluan, satu agen koordinator tambahan menegakkan kapasitas arc bersama melalui harga π_{l} yang diperbarui setiap putaran, sehingga setiap agen pod ikut \"merasakan\" kepadatan arc yang dipakai pod lain.");
FIGURE("gambar6_1_arsitektur.png", "Arsitektur MAS-QA multi-agen. Agen koordinator harga hanya dipakai pada studi pendahuluan (Subbab 6.5.6).");
H3("6.3.1 Agen dan Pembagian Arc");
P("Dekomposisi mengikuti pod sumber seperti pada bab sebelumnya, sehingga terdapat k agen pod pada Fat-Tree k. Arc dibagi menjadi dua himpunan:");
UL([
  "**Arc lokal** L_{q} — arc naik di dalam pod q (host→edge, edge→aggregation, aggregation→core), yang hanya dilalui flow bersumber dari pod q. Kapasitasnya ditegakkan di dalam QUBO pod dengan slack biner.",
  "**Arc bersama** L_{s} — arc turun (core→aggregation, aggregation→edge, edge→host) yang dapat dilalui flow dari pod mana pun menuju pod tujuan. Kapasitasnya ditegakkan oleh *repair* atau oleh harga.",
]);
P("Pembagian ini diverifikasi pada setiap topologi: tidak ada arc lokal yang dilalui flow dari lebih dari satu pod. Jumlah arc lokal dan bersama masing-masing 48 dan 48 (k = 4), 162 dan 162 (k = 6), serta 384 dan 384 (k = 8).");
H3("6.3.2 Relaksasi Lagrangian Kapasitas Bersama");
P("Kendala kapasitas arc bersama adalah Σ_{q} L_{q,l} ≤ c untuk setiap l ∈ L_{s}. Kendala ini direlaksasi dengan pengali π_{l} ≥ 0; notasi π dipakai agar tidak tertukar dengan bobot λ pada objektif. QUBO agen pod q menjadi:");
EQ("pers6_5.png");
P("Karena beban arc linear terhadap x_{f,p}, harga hanya menambah suku diagonal sebesar (d_{f}/c)·Σ π_{l} pada setiap variabel jalur. Tidak ada kopling baru, sehingga harga dapat diperbarui tanpa membangun ulang struktur QUBO.");
H3("6.3.3 Pembaruan Harga dan Stabilisasi");
P("Harga diperbarui dengan metode subgradien terproyeksi pada beban yang dirata-ratakan antar-putaran (rata-rata primal):");
EQ("pers6_6.png");
P("Dua aturan langkah diuji: langkah yang meluruh, ρ_{t} = ρ_{0}/√(t + 1), dan langkah konstan yang diskalakan terhadap reward, ρ_{0} = m × median μ_{f}. Tiga mekanisme stabilisasi ditambahkan setelah studi pendahuluan pertama menunjukkan osilasi:");
OL([
  "**Benih sampler tetap** di setiap putaran, sehingga perubahan keputusan berasal dari harga, bukan dari derau sampler.",
  "**Suku proksimal** κ(z − z_{prev})^{2} pada setiap variabel keputusan, yang untuk variabel biner tereduksi menjadi suku linear κz(1 − 2z_{prev}), dengan κ = 2.",
  "**Rata-rata primal** beban dengan α = 0,5 sebagai dasar pembaruan harga.",
]);
P("Iterasi berhenti bila kelebihan beban maksimum arc bersama tidak lebih dari 2% kapasitas, bila perubahan relatif vektor harga di bawah 10^{−3}, atau bila jumlah putaran mencapai T_{max}. Keluaran yang dipakai adalah putaran dengan jumlah flow diterima terbanyak setelah *repair*, yang dapat dihitung secara deterministik oleh *controller*. Semua keluaran tetap melewati *repair* bersama yang identik dengan bab sebelumnya, sehingga perbedaan hasil dapat diatribusikan pada koordinasi, bukan pada *repair*.");
H3("6.3.4 Posisi terhadap Literatur");
P("Dekomposisi berbasis ADMM yang menghasilkan subproblem QUBO sudah dikenal, antara lain untuk *unit commitment* terdistribusi (Nikmehr dkk., 2022). Xuan dkk. (2024) memakai relaksasi Lagrangian untuk memecah penjadwalan fungsi jaringan virtual menjadi subproblem QUBO yang diselesaikan secara paralel, mekanisme yang paling dekat dengan koordinasi harga dalam bab ini. Teknik partisi QUBO yang lebih umum dibahas oleh Verma dan Lewis (2022). Kebaruan bab ini terletak pada penerapannya untuk admisi flow SDN dengan harga pada arc bersama antar-pod Fat-Tree, integrasinya dengan reward admisi analitis, dan evaluasinya dengan kontrol derau sampler serta kontrol \"terbaik dari K restart\". Kontrol terakhir inilah yang memisahkan efek koordinasi dari efek pengambilan sampel berulang.");

// ------------------------------------------------------------------ 6.4
H2("6.4 Proteksi Prioritas Bertahap");
P("Kelas dilayani berurutan, yaitu EF lalu AF lalu BE, dengan setiap tahap hanya memakai kapasitas yang tersisa dari tahap sebelumnya. Tujuannya adalah menurunkan kehilangan EF yang pada bab sebelumnya mencapai 34–53% pada 100–150 flow, padahal penalti prioritas lunak tidak berhasil menurunkannya.");
H3("6.4.1 Prosedur");
OL([
  "**Tahap EF** — setiap agen pod hanya memuat flow EF miliknya dan menyelesaikan QUBO dengan μ_{f}. Hasilnya di-*repair*, lalu admisi EF dikunci.",
  "**Tahap AF** — beban EF yang terkunci diperlakukan sebagai beban tetap yang tidak dapat dibuang. Flow AF diselesaikan pada kapasitas sisa dengan prosedur yang sama, lalu dikunci.",
  "**Tahap BE** — flow BE diselesaikan pada kapasitas sisa.",
  "**Repair akhir** — *repair* bersama dijalankan sekali pada gabungan ketiga tahap.",
]);
P("Suku *fairness* antarkelas dimatikan (λ_{f} = 0) di setiap tahap karena satu tahap hanya memuat satu kelas. Pada implementasi awal, beban terkunci dimodelkan sebagai flow semu berprioritas tertinggi, tetapi aturan *repair* membuang flow semu itu bila arcnya kelebihan beban. Kesalahan ini ditemukan pada studi pendahuluan dan diperbaiki dengan *repair* yang memperlakukan beban terkunci sebagai pengurang kapasitas; tanpa beban terkunci, hasilnya identik dengan *repair* bab sebelumnya.");
H3("6.4.2 Ukuran Masalah dan Kerja");
P("Setiap tahap memuat sekitar 10%, 30% dan 60% flow, sehingga QUBO per tahap jauh lebih kecil daripada QUBO pod gabungan. Setiap tahap memakai jumlah sweeps per pod yang sama dengan MAS-QA-v2, dan total kerjanya tetap lebih kecil, yaitu 65–75% kerja MAS-QA-v2.");
H3("6.4.3 Hipotesis");
P("Pentahapan diperkirakan menurunkan kehilangan EF mendekati Greedy-only, sementara PL_{flow} total tetap lebih rendah daripada Greedy-only. Utilitas berbobot prioritas (bobot 3, 2 dan 1 untuk EF, AF dan BE) dilaporkan sebagai metrik pendamping, karena pada bab sebelumnya metrik ini menempatkan Greedy-only di atas MAS-QA.");

// ------------------------------------------------------------------ 6.5
H2("6.5 Desain Eksperimen");
P("Eksperimen mengikuti protokol bab sebelumnya, yaitu seed validasi dan evaluasi yang terpisah, anggaran setara dalam *spin-update*, *repair* bersama, dan uji berpasangan per seed. Evaluasi dibagi menjadi dua tingkat yang dapat dijalankan pada komputer dua core, ditambah studi pendahuluan untuk koordinasi harga.");
H3("6.5.1 Topologi dan Trafik");
TABLE("Topologi, beban dan seed yang digunakan", ["Topologi", "Host", "Arc berarah (50 Mbps)", "Jalur antar-pod", "Agen pod", "Flow", "Penggunaan"], [
  ["Fat-Tree k = 4", "16", "96", "4", "4", "50, 100, 150 (S1–S3)", "Evaluasi tingkat A, seed 42–71"],
  ["Fat-Tree k = 6", "54", "324", "9", "6", "338 (setara S2)", "Evaluasi tingkat B, seed 42–51"],
  ["Fat-Tree k = 8", "128", "768", "16", "8", "800 (setara S2)", "Studi pendahuluan, seed 100–102"],
], [2.6, 1.2, 2.0, 1.6, 1.4, 2.6, 3.4]);
P("Model trafik sama dengan bab sebelumnya: permintaan berdistribusi Pareto (bentuk 2, minimum 2 Mbps), rata-rata sekitar 12,8 Mbps per flow, dengan komposisi kelas 10% EF, 30% AF dan 60% BE. Jumlah flow pada k = 6 dan k = 8 diskalakan menurut jumlah host agar permintaan per host setara dengan S2 (sekitar 79,9 Mbps per host). Trafik k = 4 yang dibangkitkan generator umum identik dengan generator bab sebelumnya.");
H3("6.5.2 Metode yang Dibandingkan");
TABLE("Metode pada evaluasi akhir", ["Metode", "Keterangan", "Menjawab", "Tingkat"], [
  ["Greedy-only, ECMP+adm", "Acuan tanpa solver", "acuan bawah", "A, B"],
  ["MAS-QA-v2", "Pipeline bab sebelumnya: SQA per pod, μ = 0, 1 × 500 sweeps", "acuan utama", "A, B"],
  ["MAS-QA-v2 (μ = 20)", "Reward admisi empiris bab sebelumnya", "RQ6.1", "A"],
  ["MAS-QA-μ_{f}", "Reward analitis, tanpa slack arc bersama", "RQ6.1", "A, B"],
  ["MAS-QA-μ_{f}-Lex", "MAS-QA-μ_{f} dengan pentahapan EF → AF → BE", "RQ6.2", "A, B"],
  ["MAS-QA-v2, K × (500/K)", "K sampel pendek, kerja total sama: 2 × 250, 4 × 125, 8 × 62", "RQ6.4", "A (4 × 125 juga B)"],
  ["IP eksak", "HiGHS, maksimasi jumlah flow, batas 60 detik", "RQ6.5", "A, B"],
  ["SA monolitik tuned", "Data bab sebelumnya, tidak dijalankan ulang", "pembanding", "A"],
], [3.4, 5.6, 2.6, 2.4], "Koordinasi harga (RQ6.3) tidak termasuk evaluasi akhir; hasilnya berasal dari studi pendahuluan (Subbab 6.5.6).");
H3("6.5.3 Pengaturan Solver dan Anggaran");
P("Pengaturan SQA dipertahankan dari bab sebelumnya: β = 0,5, Γ = 1,0 dan P = 16 irisan Trotter, dengan 10 *reads* × 500 sweeps per pod untuk MAS-QA-v2. Kerja dihitung dalam *spin-update*, yaitu jumlah variabel × P × sweeps × *reads*. Konfigurasi K sampel memakai K × (500/K) sweeps sehingga kerja totalnya sama, lalu memilih sampel yang menerima flow terbanyak setelah *repair*. IP eksak diselesaikan dengan HiGHS melalui SciPy dengan batas waktu 60 detik; bila optimum tidak tercapai, yang dilaporkan adalah solusi terbaik beserta MIP gap. Hasil SA monolitik tuned (10 × 80.000 sweeps) dipakai ulang dari data bab sebelumnya karena seed dan trafiknya identik.");
H3("6.5.4 Protokol dan Analisis Statistik");
P("Tingkat A memakai Fat-Tree k = 4 pada S1–S3 dengan 30 seed evaluasi (42–71), sama dengan bab sebelumnya. Tingkat B memakai Fat-Tree k = 6 dengan 10 seed (42–51). Seed evaluasi tidak pernah dipakai untuk memilih pengaturan. Setiap perbandingan dilaporkan sebagai rata-rata selisih berpasangan per seed dengan interval kepercayaan (IK) 95%, uji-t berpasangan dan uji Wilcoxon *signed-rank*.");
P("Famili koreksi Bonferroni ditetapkan sebelum hasil dilihat: (i) RQ6.1, yaitu MAS-QA-μ_{f} dan MAS-QA-v2 (μ = 20) terhadap MAS-QA-v2 per skenario (enam perbandingan); (ii) RQ6.2, yaitu kehilangan EF dan PL_{flow} MAS-QA-μ_{f}-Lex terhadap MAS-QA-μ_{f} per skenario (enam perbandingan); dan (iii) RQ6.4, yaitu tiga konfigurasi K sampel terhadap 1 × 500 per skenario (sembilan perbandingan). Perbandingan pada k = 6 dan terhadap IP dilaporkan tanpa koreksi.");
H3("6.5.5 Metrik");
UL([
  "**PL**_{flow} — persentase flow yang ditolak (metrik utama).",
  "**Kehilangan per kelas** — PL_{EF}, PL_{AF} dan PL_{BE}.",
  "**Utilitas berbobot prioritas** — permintaan yang diterima dengan bobot 3, 2 dan 1 untuk EF, AF dan BE, sebagai persentase total permintaan berbobot.",
  "**Kerja annealing** — dalam *spin-update*, dan **waktu** per instans yang diukur berurutan pada satu core.",
  "**Ukuran koordinasi** (studi pendahuluan) — kelebihan beban maksimum arc bersama dan persentase variabel yang berubah per putaran.",
]);
H3("6.5.6 Studi Pendahuluan Koordinasi Harga");
P("Koordinasi harga diuji pada seed validasi sebelum evaluasi akhir: lima seed (100–104) pada k = 4 (S2) dan k = 6, serta tiga seed (100–102) pada k = 8. Studi pendahuluan berlangsung dalam empat tahap: (1) loop harga awal dengan benih sampler berbeda di setiap putaran; (2) loop harga yang distabilkan (Subbab 6.3.3), dibandingkan dengan kontrol \"MAS-QA-v2 terbaik dari 2 restart\" pada kerja yang sebanding; (3) pengulangan pada k = 6 dan k = 8; dan (4) uji keputusan dengan langkah harga konstan berskala μ_{f} (m = 3 dan 10, 10 putaran × 150 sweeps).");
P("Aturan keputusan ditetapkan sebelum tahap (4) dijalankan: koordinasi harga dipertahankan dalam evaluasi akhir hanya bila lebih baik minimal 1 pp daripada kontrol \"terbaik dari 2 restart\" pada k = 4 dan k = 6, dengan arah yang sama di minimal 4 dari 5 seed. Koordinasi tidak lolos aturan ini (Subbab 6.6.3), sehingga evaluasi akhir difokuskan pada RQ6.1, RQ6.2, RQ6.4 dan RQ6.5.");
H3("6.5.7 Lingkungan Komputasi");
P("Semua eksperimen dijalankan pada mesin dua core (Intel Xeon 2,1 GHz, 7 GB RAM) dengan Python 3.13, NumPy 2.5, SciPy 1.18.1 (termasuk HiGHS), pandas 3.0 dan OpenJij 0.12.2. Evaluasi tingkat A membutuhkan sekitar 2 menit per seed untuk ketiga skenario, dan tingkat B sekitar 2 menit per seed; dengan kedua tingkat dijalankan bersamaan, total waktu sekitar satu jam. Kode, data dan skrip analisis tersedia pada cabang bab6 repositori QA-SDN_source_code.");

// ------------------------------------------------------------------ 6.6
H2("6.6 Hasil");
P("Sebagai pemeriksaan silang, MAS-QA-v2 yang dijalankan ulang menghasilkan PL_{flow} 20,5; 41,3 dan 54,0% pada S1–S3, sama persis dengan bab sebelumnya. Selisihnya terhadap IP eksak (4,7; 8,5 dan 8,9 pp) dan terhadap SA tuned juga sama dengan yang dilaporkan di sana.");
H3("6.6.1 Reward Admisi Analitis (RQ6.1)");
P("Reward admisi analitis μ_{f} memberi kualitas setara MAS-QA-v2 dengan 40–49% kerja annealing, sedangkan μ = 20 empiris memberi kualitas sedikit lebih baik dengan kerja penuh (Tabel 6.4 dan Gambar 6.2).");
TABLE("PL_{flow} (%) dan selisih berpasangan terhadap MAS-QA-v2 untuk reward admisi", ["Skenario", "MAS-QA-v2", "μ_{f} analitis", "Selisih μ_{f} (pp)", "μ = 20", "Selisih μ = 20 (pp)", "Kerja μ_{f} / v2"], [
  ["S1 (50 flow)", "20,5", "19,9", "−0,6 [−2,1; +0,9] p_{adj} = 1,00", "19,6", "−0,9 [−1,7; −0,1] p_{adj} = 0,21", "0,40"],
  ["S2 (100 flow)", "41,3", "40,6", "−0,7 [−1,8; +0,3] p_{adj} = 0,96", "39,5", "−1,8 [−2,6; −1,0] p_{adj} < 0,001", "0,44"],
  ["S3 (150 flow)", "54,0", "53,9", "−0,1 [−0,7; +0,5] p_{adj} = 1,00", "52,3", "−1,7 [−2,3; −1,1] p_{adj} < 0,001", "0,49"],
  ["k = 6 (338 flow)", "39,8", "39,9", "+0,1 [−0,7; +0,9] p = 0,69", "–", "–", "0,46"],
], [2.4, 1.6, 1.6, 3.0, 1.3, 3.0, 1.6], "Angka dalam kurung siku adalah IK 95%. p_{adj}: Bonferroni atas enam perbandingan famili RQ6.1. Negatif berarti lebih sedikit flow hilang.");
P("Penghematan kerja berasal dari penghapusan slack biner pada arc bersama di QUBO pod. Di sisi lain, μ = 20 menaikkan kehilangan EF (S2: 40,0% dibanding 34,3%; S3: 60,0% dibanding 53,1%), karena reward yang seragam mendorong penerimaan flow kecil yang umumnya berkelas BE.");
FIGURE("gambar6_2_reward_admisi.png", "(a) Selisih PL_{flow} terhadap MAS-QA-v2 dengan IK 95% (30 seed pada k = 4, 10 seed pada k = 6). (b) Kerja annealing μ_{f} sebagai persentase kerja MAS-QA-v2.");
H3("6.6.2 Proteksi Prioritas Bertahap (RQ6.2)");
P("Pentahapan EF → AF → BE menurunkan kehilangan EF secara besar dan konsisten, dengan biaya kenaikan PL_{flow} total 2,5–2,9 pp pada beban tinggi (Tabel 6.5 dan Gambar 6.3).");
TABLE("Kehilangan EF, PL_{flow} dan utilitas berbobot prioritas: MAS-QA-μ_{f} dibanding MAS-QA-μ_{f}-Lex", ["Skenario", "PL_{EF} μ_{f} (%)", "PL_{EF} Lex (%)", "Selisih EF (pp)", "Selisih PL_{flow} (pp)", "Utilitas prioritas μ_{f} → Lex (%)"], [
  ["S1", "18,0", "2,0", "−16,0; p_{adj} < 0,001", "+0,2; p_{adj} = 1,00", "67,8 → 73,1"],
  ["S2", "37,0", "3,0", "−34,0; p_{adj} < 0,001", "+2,5; p_{adj} = 0,005", "46,6 → 56,5"],
  ["S3", "56,4", "4,2", "−52,2; p_{adj} < 0,001", "+2,9; p_{adj} < 0,001", "33,0 → 44,3"],
  ["k = 6", "48,2", "5,0", "−43,2; p < 0,001", "+2,9; p = 0,004", "42,8 → 54,7"],
], [2.1, 1.9, 1.9, 2.8, 2.8, 3.0], "p_{adj}: Bonferroni atas enam perbandingan famili RQ6.2.");
P("Pada S2 dan S3, kehilangan EF turun di 30 dari 30 seed. Utilitas berbobot prioritas Lex mendekati Greedy-only (S2: 56,5% dibanding 56,9%), tetapi PL_{flow}-nya jauh lebih rendah (43,1% dibanding 49,1%). Lex dengan demikian menempati posisi tengah: hampir seprotektif Greedy-only terhadap EF, dengan kehilangan total yang mendekati pipeline berbasis solver.");
FIGURE("gambar6_3_proteksi_prioritas.png", "Kehilangan flow per kelas untuk MAS-QA-μ_{f} dan MAS-QA-μ_{f}-Lex. Angka di atas batang EF adalah rata-rata kehilangan EF (%).");
H3("6.6.3 Koordinasi Harga Antar-Agen (RQ6.3)");
P("Koordinasi harga antar-agen pod tidak menambah kualitas di atas *repair* bersama pada ketiga ukuran Fat-Tree yang diuji. Hasil ini berasal dari studi pendahuluan pada seed validasi (Subbab 6.5.6).");
TABLE("Ringkasan koordinasi harga stabil pada seed validasi", ["Topologi", "Seed", "Harga stabil − MAS-QA-v2 (pp)", "Seed harga lebih baik", "Harga stabil − terbaik dari 2 restart (pp)", "Harga adaptif − terbaik dari 2 restart (pp)"], [
  ["k = 4", "5", "+0,2", "1 dari 5", "+0,6", "+1,4 sampai +2,0"],
  ["k = 6", "5", "−0,5", "3 dari 5", "+0,5", "+0,7 sampai +1,3"],
  ["k = 8", "3", "+0,8", "0 dari 3", "+1,0", "tidak diuji"],
], [2.0, 1.3, 2.7, 2.2, 3.0, 3.0], "Nilai positif berarti koordinasi kehilangan lebih banyak flow. Harga adaptif: langkah konstan ρ_{0} = m × median μ_{f}, m = 3 dan 10.");
P("Tiga pengamatan menjelaskan hasil ini:");
OL([
  "**Osilasi awal adalah derau sampler.** Dengan benih sampler berbeda di setiap putaran, sekitar 65% variabel berubah per putaran, dan memilih putaran terbaik memberi kesan perbaikan 1,6 pp pada k = 4. Dengan benih tetap, perubahan turun di bawah 1–2% per putaran dan perbaikan itu hilang; hasil putaran terakhir varian acak sama dengan MAS-QA-v2.",
  "**Harga menurunkan kelebihan beban, tetapi tidak menambah flow.** Kelebihan beban maksimum arc bersama turun dari 94% menjadi 27% di atas kapasitas (k = 4) dan dari 130% menjadi 40% (k = 6, langkah adaptif m = 10). Jumlah flow yang diterima setelah *repair* tetap sama, karena *repair* menyelesaikan konflik yang sama secara deterministik.",
  "**Sebagian konflik hanya dapat diselesaikan dengan admisi.** Delapan dari 16 arc bersama yang masih kelebihan beban di putaran akhir (k = 4, lima seed) adalah arc edge→host. Semua jalur menuju satu host melewati arc tersebut, sehingga rute tidak dapat menghindarinya.",
]);
P("Pada uji keputusan, kedua varian langkah adaptif lebih buruk daripada kontrol restart di kelima seed k = 4, dan tetap lebih buruk 0,7–1,3 pp pada k = 6. Sesuai aturan yang ditetapkan sebelumnya, koordinasi harga tidak dimasukkan ke evaluasi akhir.");
FIGURE("gambar6_4_koordinasi_harga.png", "Koordinasi harga stabil pada seed validasi. (a) Kelebihan beban maksimum arc bersama per putaran. (b) Selisih PL_{flow} terhadap MAS-QA-v2 dan terhadap kontrol \"terbaik dari 2 restart\" dengan IK 95%; positif berarti koordinasi kehilangan lebih banyak flow.");
H3("6.6.4 Alokasi Anggaran Annealing (RQ6.4)");
P("Pada k = 4, membagi anggaran yang sama menjadi lebih banyak sampel pendek menurunkan PL_{flow} secara signifikan; pada k = 6, efek ini tidak muncul (Tabel 6.7 dan Gambar 6.5).");
TABLE("Selisih PL_{flow} (pp) terhadap 1 × 500 sweeps per pod pada kerja total yang sama", ["Skenario", "2 × 250", "4 × 125", "8 × 62"], [
  ["S1", "−0,9; p_{adj} = 0,82", "−2,0; p_{adj} = 0,013", "−2,9; p_{adj} < 0,001"],
  ["S2", "−1,1; p_{adj} = 0,51", "−1,6; p_{adj} = 0,008", "−1,9; p_{adj} < 0,001"],
  ["S3", "−0,4; p_{adj} = 1,00", "−0,6; p_{adj} = 0,74", "−1,1; p_{adj} = 0,006"],
  ["k = 6", "–", "+0,1; p = 0,89", "–"],
], [2.0, 4.0, 4.0, 4.0], "Negatif berarti lebih sedikit flow hilang. p_{adj}: Bonferroni atas sembilan perbandingan famili RQ6.4.");
P("Konfigurasi 8 × 62 sweeps lebih baik daripada MAS-QA-v2 di ketiga skenario k = 4, dan rata-ratanya pada S2 dan S3 (39,4% dan 52,9%) juga di bawah SA monolitik tuned dari bab sebelumnya (42,5% dan 55,8%). Efeknya mengecil seiring beban (−2,9 menjadi −1,1 pp) dan hilang pada k = 6, ketika QUBO pod jauh lebih besar (sekitar 1.450 variabel per pod dibanding sekitar 420 pada k = 4 S2), sehingga sampel 125 sweeps kemungkinan terlalu pendek untuk mencapai solusi yang baik.");
FIGURE("gambar6_5_alokasi_anggaran.png", "Selisih PL_{flow} terhadap 1 × 500 sweeps per pod pada kerja total yang sama, dengan IK 95% (30 seed per skenario k = 4; 10 seed pada k = 6).");
H3("6.6.5 Perbandingan dengan IP Eksak (RQ6.5)");
P("IP eksak menerima lebih banyak flow daripada pipeline multi-agen pada semua ukuran yang diuji, sehingga titik silang kualitas tidak tercapai. Yang berubah adalah waktunya: IP melambat jauh lebih cepat daripada pipeline (Tabel 6.8 dan Gambar 6.6).");
TABLE("Perbandingan MAS-QA-v2 dengan IP eksak", ["Skenario", "IP − MAS-QA-v2 (pp)", "IP optimal dalam 60 detik", "Waktu IP rata-rata (detik)", "Waktu MAS-QA-v2 (detik)"], [
  ["S1", "−4,7 [−5,9; −3,5]", "30 dari 30", "0,06", "3,6"],
  ["S2", "−8,5 [−9,5; −7,5]", "30 dari 30", "2,9", "4,2"],
  ["S3", "−8,9 [−9,5; −8,3]", "22 dari 30 (gap rata-rata 0,4%)", "33,5", "4,7"],
  ["k = 6", "−6,9 [−7,8; −6,0]", "0 dari 10 (gap rata-rata 2,0%)", "60,0 (batas)", "20,4"],
], [1.8, 3.2, 3.6, 2.8, 2.6], "Waktu MAS-QA-v2 diukur berurutan pada satu core.");
P("Bila pod dijalankan paralel, waktu pipeline turun mendekati waktu satu pod. Titik silang waktu sudah terlewati pada S3 dan k = 6, tetapi pada batas 60 detik IP masih menemukan solusi yang lebih baik daripada pipeline, meskipun belum terbukti optimal.");
FIGURE("gambar6_6_ip_eksak.png", "(a) PL_{flow} rata-rata MAS-QA-v2 dan IP eksak; angka menunjukkan selisih IP − MAS-QA-v2 (pp). (b) Waktu per instans pada skala logaritmik.");

// ------------------------------------------------------------------ 6.7
H2("6.7 Pembahasan");
P("Hasil bab ini menggeser letak nilai MAS-QA: bukan pada kualitas solver atau negosiasi antar-agen, melainkan pada dekomposisi yang murah, aturan global yang deterministik, dan cara anggaran annealing dipakai.");
H3("6.7.1 Repair Bersama sebagai Koordinator Implisit");
P("Hasil RQ6.3 menunjukkan bahwa dalam arsitektur MAS-QA, koordinasi antar-agen sudah terjadi secara implisit di *repair* bersama, sehingga koordinasi eksplisit melalui harga tidak menambah nilai. *Repair* menerima keputusan semua agen pod sekaligus dan menyelesaikan setiap konflik arc bersama secara deterministik menurut urutan prioritas. Harga hanya menggeser keputusan agen ke keadaan yang toh akan dicapai *repair*, dengan biaya beberapa putaran annealing tambahan.");
P("Implikasinya bagi desain sistem multi-agen pada SDN: nilai pendekatan multi-agen terletak pada dekomposisi masalah (QUBO per pod lebih kecil dan dapat dijalankan paralel) dan pada aturan global yang deterministik, bukan pada negosiasi berulang antar-agen. Koordinasi eksplisit baru layak dipertimbangkan bila tidak ada titik kontrol global yang dapat menjalankan *repair*, misalnya pada kontrol terdistribusi multi-*controller*, yang berada di luar cakupan disertasi ini.");
H3("6.7.2 Reward Analitis dibanding Reward Empiris");
P("Reward μ_{f} analitis dan μ = 20 empiris menjawab kebutuhan yang berbeda. μ_{f} dihitung sebelum solver dijalankan tanpa grid pencarian, dan memungkinkan penghapusan slack arc bersama sehingga kerja turun menjadi 40–49%. μ = 20 memerlukan seed validasi untuk dipilih, tetapi memberi 1,7–1,8 pp lebih sedikit flow yang hilang pada S2 dan S3.");
P("Selisih itu dapat dijelaskan dari besarnya reward. Median μ_{f} pada k = 4 sekitar 4, jauh di bawah 20, karena μ_{f} adalah reward minimum yang cukup agar admisi menurunkan energi. Reward seragam yang lebih besar mendorong solver menerima lebih banyak flow, tetapi yang terdorong terutama flow kecil kelas BE, sehingga kehilangan EF naik 5–7 pp. Kombinasi yang belum diuji, yaitu μ_{f} dikalikan faktor skala tunggal dan digabung dengan pentahapan prioritas, berpotensi memperoleh kedua keuntungan.");
H3("6.7.3 Proteksi Prioritas dan Pilihan Desain");
P("Pentahapan EF → AF → BE berhasil di tempat penalti lunak gagal. Bab sebelumnya menunjukkan bahwa penalti prioritas lunak tidak menurunkan kehilangan EF, sedangkan pentahapan menurunkannya ke 2–5% di semua skenario. Perbedaannya mendasar: penalti lunak hanya menambah biaya energi yang dapat dikalahkan suku lain, sedangkan pentahapan menjamin kapasitas untuk EF sudah dikunci sebelum kelas lain dipertimbangkan.");
P("Pilihan metode bergantung pada kebutuhan layanan. Bila jaminan untuk lalu lintas EF menjadi syarat, Lex memberi proteksi hampir setara Greedy-only dengan kehilangan total 6 pp lebih rendah (S2). Bila yang diutamakan adalah jumlah flow total, MAS-QA dengan μ = 20 atau dengan delapan sampel pendek lebih tepat, dengan kehilangan EF 16–60% tergantung beban. Pendekatan pembelajaran penguatan untuk QoS pada SDN, misalnya Xia dkk. (2022), berfokus pada pemilihan jalur yang menyeimbangkan latensi dan beban; pentahapan prioritas bersifat komplementer karena bekerja pada tingkat admisi.");
H3("6.7.4 Mengapa Banyak Sampel Pendek Lebih Baik pada k = 4");
P("Efek alokasi anggaran konsisten dengan temuan bab sebelumnya bahwa sampel solver berfungsi sebagai titik awal bagi *repair*, bukan sebagai solusi akhir. Bila hasil akhir ditentukan oleh *repair*, keragaman titik awal lebih berharga daripada kedalaman pencarian satu sampel: delapan sampel 62 sweeps memberi *repair* delapan titik awal berbeda, sedangkan satu sampel 500 sweeps hanya memberi satu.");
P("Efek ini hilang pada k = 6, ketika QUBO pod membesar sekitar 3,5 kali. Sampel yang terlalu pendek tidak lagi mencapai solusi yang layak sebagai titik awal, sehingga keragaman tidak menutup penurunan kualitas per sampel. Jumlah sampel optimal kemungkinan bergantung pada ukuran QUBO pod, sehingga jumlah sampel dan panjang sweep sebaiknya disetel bersama pada seed validasi untuk setiap ukuran topologi.");
P("Temuan ini sejalan dengan pengamatan bahwa kinerja annealer sangat bergantung pada pengaturan dan anggaran sampel, sehingga perbandingan antar-solver perlu menyetarakan keduanya (King dkk., 2023; Vert dkk., 2024). Pemecah terinspirasi fisika lainnya, seperti *simulated bifurcation* (Goto dkk., 2021) dan jaringan saraf graf (Schuetz dkk., 2022), dapat diuji dengan protokol yang sama pada penelitian lanjutan.");
H3("6.7.5 Posisi terhadap Metode Eksak dan Keterbatasan");
P("Pada ukuran yang diuji, IP eksak dengan batas 60 detik selalu menerima lebih banyak flow daripada pipeline multi-agen, sehingga klaim bahwa pipeline lebih baik daripada metode eksak tidak didukung. Yang didukung adalah klaim yang lebih sempit: waktu IP naik jauh lebih cepat (0,06 detik pada S1 hingga batas 60 detik pada k = 6), sedangkan pipeline tetap beberapa detik dan dapat diparalelkan per pod. Pipeline layak dipertimbangkan bila ada batas waktu keputusan yang ketat, atau sebagai solusi awal bagi IP.");
P("Hasil ini berbeda dengan Şeker dkk. (2024), yang melaporkan bahwa *Digital Annealer* umumnya menyamai atau melampaui Gurobi dalam dua menit untuk masalah perutean dan penetapan panjang gelombang dengan proteksi. Perbedaan tersebut kemungkinan berasal dari struktur masalah dan jenis pemecah yang dipakai, sehingga keunggulan annealer terhadap metode eksak tidak dapat digeneralisasi tanpa uji pada masalah yang sama.");
P("Keterbatasan bab ini adalah sebagai berikut:", { indent: { firstLine: 0 } });
UL([
  "Semua solver adalah simulasi klasik pada CPU; tidak ada klaim perangkat keras kuantum.",
  "Trafik bersifat statis dan metrik bersifat *surrogate* (flow utuh diterima atau ditolak).",
  "Fat-Tree k = 8 dan koordinasi harga hanya diuji pada seed validasi, tidak pada seed evaluasi.",
  "μ_{f} pada evaluasi akhir dihitung dengan beban latar nol, dan verifikasi enumerasi lengkap untuk QUBO dengan μ_{f} belum dilakukan.",
  "Batas waktu IP 60 detik, sehingga pada S3 dan k = 6 sebagian solusi IP belum terbukti optimal (gap 0,4–2,0%).",
  "Waktu diukur berurutan pada satu mesin dua core; waktu paralel tidak diukur.",
  "Pada k = 6 hanya 10 seed yang dijalankan, sehingga daya uji lebih rendah daripada tingkat A.",
]);

// ------------------------------------------------------------------ 6.8
H2("6.8 Ringkasan Bab");
P("Bab ini menghasilkan lima jawaban, masing-masing dengan batasnya:", { indent: { firstLine: 0 } });
OL([
  "**RQ6.1** — Reward admisi analitis μ_{f} menghilangkan kebutuhan mencari μ secara empiris dan memberi kualitas setara MAS-QA-v2 dengan 40–49% kerja annealing, tetapi μ = 20 empiris tetap 1,7–1,8 pp lebih baik pada S2 dan S3.",
  "**RQ6.2** — Pentahapan prioritas menurunkan kehilangan EF sebesar 16–52 pp (menjadi 2–5%), dengan biaya PL_{flow} total +2,5–2,9 pp pada beban tinggi dan kenaikan utilitas berbobot prioritas 5–12 poin.",
  "**RQ6.3** — Koordinasi harga antar-agen tidak menambah kualitas di atas *repair* bersama pada k = 4, 6 dan 8, karena *repair* berfungsi sebagai koordinator implisit.",
  "**RQ6.4** — Pada k = 4, membagi anggaran annealing menjadi delapan sampel pendek menurunkan PL_{flow} 1,1–2,9 pp; efek ini hilang pada k = 6.",
  "**RQ6.5** — IP eksak tetap 4,7–8,9 pp lebih baik pada semua ukuran yang diuji, tetapi waktunya naik dari 0,06 detik (S1) ke batas 60 detik (k = 6), sedangkan pipeline tetap 3,6–20 detik secara berurutan.",
]);
P("Bab penutup menggabungkan temuan ini dengan bab-bab sebelumnya. Kesimpulan besarnya: nilai MAS-QA terletak pada dekomposisi dan proteksi prioritas yang murah dan dapat diparalelkan, bukan pada keunggulan kualitas solver atau koordinasi antar-agen.");


H2("Daftar Pustaka");
const REFS = [
  "Bhavanasi, S. S., Pappone, L., & Esposito, F. (2023). Dealing with changes: Resilient routing via graph neural networks and multi-agent deep reinforcement learning. *IEEE Transactions on Network and Service Management, 20*(3), 2283–2294. https://doi.org/10.1109/TNSM.2023.3287936",
  "Chen, J., Date, P., Chancellor, N., Atiquzzaman, M., & Sreenan, C. (2022). Controller-based energy-aware wireless sensor network routing using quantum algorithms. *IEEE Transactions on Quantum Engineering, 3*, Artikel 3102912. https://doi.org/10.1109/TQE.2022.3217297",
  "Chiavassa, P., Marchesin, A., Pedone, I., Ferrari Dacrema, M., & Cremonesi, P. (2022). Virtual network function embedding with quantum annealing. Dalam *2022 IEEE International Conference on Quantum Computing and Engineering (QCE)* (hlm. 282–291). IEEE. https://doi.org/10.1109/QCE53715.2022.00048",
  "Glover, F., Kochenberger, G., Hennig, R., & Du, Y. (2022). Quantum bridge analytics I: A tutorial on formulating and using QUBO models. *Annals of Operations Research, 314*(1), 141–183. https://doi.org/10.1007/s10479-022-04634-2",
  "Goto, H., Endo, K., Suzuki, M., Sakai, Y., Kanao, T., Hamakawa, Y., Hidaka, R., Yamasaki, M., & Tatsumura, K. (2021). High-performance combinatorial optimization based on classical mechanics. *Science Advances, 7*(6), eabe7953. https://doi.org/10.1126/sciadv.abe7953",
  "Hamdan, M., Hassan, E., Abdelaziz, A., Elhigazi, A., Mohammed, B., Khan, S., Vasilakos, A. V., & Marsono, M. N. (2021). A comprehensive survey of load balancing techniques in software-defined network. *Journal of Network and Computer Applications, 174*, Artikel 102856. https://doi.org/10.1016/j.jnca.2020.102856",
  "Inoue, D., Okada, A., Matsumori, T., Aihara, K., & Yoshida, H. (2021). Traffic signal optimization on a square lattice with quantum annealing. *Scientific Reports, 11*, Artikel 3303. https://doi.org/10.1038/s41598-021-82740-0",
  "King, A. D., Raymond, J., Lanting, T., Harris, R., Zucca, A., Altomare, F., dkk. (2023). Quantum critical dynamics in a 5,000-qubit programmable spin glass. *Nature, 617*(7959), 61–66. https://doi.org/10.1038/s41586-023-05867-2",
  "Mohseni, N., McMahon, P. L., & Byrnes, T. (2022). Ising machines as hardware solvers of combinatorial optimization problems. *Nature Reviews Physics, 4*(6), 363–379. https://doi.org/10.1038/s42254-022-00440-8",
  "Montañez-Barrera, J. A., Willsch, D., Maldonado-Romo, A., & Michielsen, K. (2024). Unbalanced penalization: A new approach to encode inequality constraints of combinatorial problems for quantum optimization algorithms. *Quantum Science and Technology, 9*(2). https://doi.org/10.1088/2058-9565/ad35e4",
  "Nikmehr, N., Zhang, P., & Bragin, M. A. (2022). Quantum distributed unit commitment: An application in microgrids. *IEEE Transactions on Power Systems, 37*(5). https://doi.org/10.1109/TPWRS.2022.3141794",
  "Schuetz, M. J. A., Brubaker, J. K., & Katzgraber, H. G. (2022). Combinatorial optimization with physics-inspired graph neural networks. *Nature Machine Intelligence, 4*(4), 367–377. https://doi.org/10.1038/s42256-022-00468-6",
  "Şeker, O., Bodur, M., & Pouya, H. (2024). Routing and wavelength assignment with protection: A quadratic unconstrained binary optimization approach enabled by Digital Annealer technology. *IISE Transactions, 56*(2), 156–171. https://doi.org/10.1080/24725854.2023.2193835",
  "Tsai, T. H., Chen, Y. C., & Nien, C. F. (2023). Network bandwidth utilization optimization with quantum-inspired approach. *SPIN, 13*(4), Artikel 2340015. https://doi.org/10.1142/S2010324723400155",
  "Verma, A., & Lewis, M. (2022). Penalty and partitioning techniques to improve performance of QUBO solvers. *Discrete Optimization, 44*, Artikel 100594. https://doi.org/10.1016/j.disopt.2020.100594",
  "Vert, D., Willsch, M., Yenilen, B., Sirdey, R., Louise, S., & Michielsen, K. (2024). Benchmarking quantum annealing with maximum cardinality matching problems. *Frontiers in Computer Science, 6*, Artikel 1286057. https://doi.org/10.3389/fcomp.2024.1286057",
  "Witt, A., Kim, J., Körber, C., & Luu, T. (2024). ILP-based resource optimization realized by quantum annealing for optical wide-area communication networks—A framework for solving combinatorial problems of a real-world application by quantum annealing. *Frontiers in Computer Science, 6*, Artikel 1356983. https://doi.org/10.3389/fcomp.2024.1356983",
  "Xia, D., Wan, J., Xu, P., & Tan, J. (2022). Deep reinforcement learning-based QoS optimization for software-defined factory heterogeneous networks. *IEEE Transactions on Network and Service Management, 19*(4), 4058–4068. https://doi.org/10.1109/TNSM.2022.3208342",
  "Xuan, W., Zhao, Z., Fan, L., & Han, Z. (2024). Lagrangian relaxation based parallelized quantum annealing and its application in network function virtualization. *IEEE Open Journal of the Communications Society, 5*, 4260–4274. https://doi.org/10.1109/OJCOMS.2024.3424433",
  "Yarkoni, S., Raponi, E., Bäck, T., & Schmitt, S. (2022). Quantum annealing for industry applications: Introduction and review. *Reports on Progress in Physics, 85*, Artikel 104001. https://doi.org/10.1088/1361-6633/ac8c54",
  "Ye, M., Zhang, J., Guo, Z., & Chao, H. J. (2023). FlexDATE: Flexible and disturbance-aware traffic engineering with reinforcement learning in software-defined networks. *IEEE/ACM Transactions on Networking, 31*(4), 1433–1448. https://doi.org/10.1109/TNET.2022.3217083",
];
REFS.forEach((r) => body.push(new Paragraph({ children: runs(r), alignment: AlignmentType.LEFT,
  indent: { left: 720, hanging: 720 }, spacing: { line: 276, after: 160 } })));

// =====================================================================  DOKUMEN
const doc = new Document({
  creator: "Welnof Satria", title: "BAB VI", description: "Disertasi MAS-QA-SDN, BAB VI",
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
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log("ditulis", OUT, b.length, "byte; tabel", tabNo, "gambar", figNo, "persamaan", eqNo); });
