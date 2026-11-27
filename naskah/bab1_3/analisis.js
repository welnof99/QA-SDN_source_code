// Catatan analisis BAB IV-VI dan proposal BAB I-III. Pemakaian: node analisis.js <keluaran.docx>
const path = require("path");
const { Paragraph, TextRun, AlignmentType, HeadingLevel } = require("docx");
const { makeDoc } = require("./lib_bab");
const D = makeDoc(path.join(__dirname, "..", "..", "figures", "bab1_3"), {});
const { P, PN, H2, H3, OL, UL, TABLE, setChapter, body } = D;
setChapter("A");
body.push(new Paragraph({ heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: "CATATAN ANALISIS BAB IV–VI DAN PROPOSAL BAB I–III", bold: true, font: "Times New Roman", size: 28 })] }));
PN("Disertasi MAS-QA-SDN · Welnof Satria · disusun 27 November 2026");

H2("1. Ringkasan");
P("Empat berkas dianalisis: proposal BAB I–III (acuan), BAB IV, BAB V, dan BAB VI. Isi BAB IV, BAB V, dan BAB VI identik dengan versi yang diunggah sebelumnya (tidak ada baris yang berbeda). BAB VI identik dengan naskah yang disusun sebelumnya; perbedaannya hanya artefak format (judul bab tidak tebal).");
P("Temuan utama ada tiga. Pertama, **proposal BAB I–III tidak lagi sesuai dengan BAB V dan BAB VI**: abstrak, permasalahan, tujuan, dan keaslian penelitian masih memuat hasil versi lama (tujuh pembanding termasuk MADDPG, GNN+RL, dan PPO; keunggulan energi 41,27%; percepatan 4,0×; konsistensi 99,9%; enam hipotesis) yang tidak ada di BAB V dan BAB VI sekarang. Kedua, **BAB IV memakai model dan protokol yang berbeda dari BAB V–VI** dan memuat beberapa klaim yang tidak didukung datanya sendiri, sehingga perlu diposisikan ulang sebagai studi eksploratif. Ketiga, **gaya sitasi dan istilah belum seragam** antarbab. Draf BAB I–III yang baru menyelesaikan masalah pertama dan menyiapkan dasar untuk masalah kedua dan ketiga.");

H2("2. Alur Antarbab");
P("Ketiga bab hasil membentuk alur yang logis bila dibaca sebagai tiga tahap:");
TABLE("Alur tiga tahap penelitian", ["Tahap", "Pertanyaan", "Temuan inti", "Yang mendorong tahap berikutnya"], [
  ["BAB IV – eksploratif", "Apakah QUBO + SQA kompetitif dibanding DQN, ACO, GA?", "SQA *throughput* terbaik (691,24 Mbps); ACO *latency* terbaik (1,4655 ms); GA *packet loss* (35%) dan JFI (0,9500) terbaik", "anggaran tidak setara, satu seed, tanpa *repair* bersama, tanpa uji berpasangan"],
  ["BAB V – terkontrol", "Apakah SQA > SA bila empat faktor disetarakan?", "SQA −1,6/−2,4 pp (S2/S3) dengan objektif baseline; berbalik dengan μ = 20; *repair* dominan; EF hilang 34–53%; IP 4,7–9,0 pp lebih baik", "objektif “tolak semua”, EF tak terlindungi, agen pod tidak saling melihat"],
  ["BAB VI – pengembangan", "Apakah μ_{f}, Lex, harga, dan alokasi anggaran memperbaiki MAS-QA?", "μ_{f}: kualitas setara dengan 40–49% kerja; Lex: EF 2–5%; harga: tidak menambah kualitas; 8 sampel pendek −1,1 sampai −2,9 pp pada k = 4", "sintesis di BAB VII"],
], [2.6, 3.6, 5.0, 3.8]);
P("Agar alur ini terbaca, BAB I–III harus menyatakannya secara eksplisit. Draf baru melakukannya melalui Gambar 1.1 (peta jalan), Tabel 1.1 (pemetaan permasalahan–bab), Tabel 3.4 (perbedaan formulasi Tahap 1 dan Tahap 2–3), dan Gambar 3.1 (alur penelitian).");

H2("3. Proposal BAB I–III (Berkas Acuan)");
H3("3.1 Ketidaksesuaian dengan BAB V dan BAB VI");
TABLE("Isi proposal yang tidak sesuai dengan bab hasil saat ini", ["Lokasi di proposal", "Isi proposal", "Kondisi di BAB V/VI saat ini"], [
  ["Abstrak; 1.2 butir 2–3; 1.3 butir 2–3; 1.6 butir 2–3", "tujuh pembanding: SA, MADDPG, GNN+RL, PPO, ACO, GA, ECMP", "BAB V membandingkan ECMP-hash, ECMP+adm, Greedy, SA (disetel/bawaan), SQA, MAS+SA, MAS-QA, ITER, IP, tabu, PT; tidak ada MADDPG, GNN+RL, PPO"],
  ["Abstrak; 1.3 butir 3; 1.6 butir 3", "keunggulan energi SQA 41,27% atas SA", "BAB V: energi bukan ukuran peringkat; objektif baseline minimum pada “tolak semua”; keunggulan SQA hilang setelah kalibrasi"],
  ["Abstrak; Tabel 3.2; 1.6 butir 3", "percepatan dekomposisi 4,0×, overhead 0,9 ms", "BAB V: pipeline memakai ±1/6 kerja *annealing*, tetapi tidak lebih cepat dalam waktu dinding (1,5 s vs 1,2 s)"],
  ["Abstrak; 1.6 butir 3", "konsistensi 99,9% pada 15 dari 19 poin; enam hipotesis", "tidak ada di BAB V/VI"],
  ["Tabel 3.2; 1.2 butir 3", "λ = (10, 5, 3, 2, 1); 1.600 variabel untuk S2; *over-subscription* 0,80×/1,60×/2,40×", "BAB V: λ = (10, 10, 5, 3, 2, 1), variabel y_{f}, x_{f,p}, s_{l,k}; skenario dinyatakan dengan jumlah flow dan Mbps"],
  ["Abstrak; 1.3 butir 2", "uji Cohen's d", "BAB V tidak melaporkan Cohen's d; memakai uji-t berpasangan, Wilcoxon, *bootstrap*, permutasi, Bonferroni"],
  ["Daftar isi", "judul dan subbab BAB V (Formulasi Algoritma LB … MAS) dan BAB VI (MAS-QA-SDN …)", "judul dan subbab berbeda; daftar isi perlu dibuat ulang dari berkas bab"],
  ["Tabel 3.2", "ECMP: “deterministik, round-robin, tanpa capacity check”", "ECMP berbasis hash; ECMP+adm memeriksa kapasitas"],
], [3.6, 5.0, 6.4], null, { size: 18 });
P("Karena itu, **abstrak proposal juga harus ditulis ulang** setelah BAB VII selesai; abstrak saat ini memuat klaim yang tidak didukung oleh bab hasil.");
H3("3.2 Kesalahan dan Kelemahan Internal Proposal");
UL([
  "Judul memuat salah ketik “*Nertwork*” (seharusnya *Network*) di sampul, lembar pengesahan, dan kata pengantar.",
  "NPM tertulis 2309300060022; mohon pastikan kembali dengan data akademik, karena NPM yang pernah Anda sebutkan adalah 2209300060022.",
  "Tabel 3.1 menulis “27 node (20 switch dan 7 host)”, sedangkan topologi yang sama di bagian lain adalah 36 node (20 *switch* dan 16 host).",
  "Batasan butir 4 menyatakan penelitian “tidak mencakup skenario data center”, padahal Fat-Tree adalah topologi pusat data. Draf baru menuliskan batasan pada k = 4, 6, 8 dan bukan skala produksi.",
  "Bahan memakai Windows 10 sedangkan alat memakai Windows 11; batasan menyebut “Python Agent Framework” yang tidak dipakai di bab hasil.",
  "Gambar 2.4 dipakai dua kali (Load Balancing SDN dan Quantum Circuit); Gambar 2.2 diambil dari ResearchGate dan Gambar 2.3 dari situs web, sehingga berisiko hak cipta. Draf baru memakai gambar buatan sendiri.",
  "Persamaan 2.1–2.3 (*throughput*, *delay*, *jitter*) berupa gambar yang tidak terbaca dalam teks; persamaan 2.5 memakai simbol “o” untuk operator Pauli.",
  "Pernyataan “dengan A(0) = B(0) dan A(t) = B(t)” pada konsep *quantum annealing* keliru; seharusnya A(0) ≫ B(0) dan A(T) ≪ B(T).",
  "Klaim bahwa *quantum annealing* “telah terbukti efektif” dan “lebih efisien” tanpa syarat bertentangan dengan temuan BAB V.",
]);
H3("3.3 Daftar Pustaka Proposal");
P("Dari 68 entri, banyak yang rusak atau tidak relevan. Entri yang rusak antara lain [8] (tanpa jurnal), [18], [20], [23], [30], [31], [44], [53], [58], [64], [66] (judul diawali “uantum Engineering”), [59] (judul “Undergraduate Program”), dan [60] (teks “Pr ep rin t”). Banyak entri tidak terkait topik, misalnya diagnosis isolasi tegangan tinggi [40], alokasi tambatan kapal [42], perencanaan UAS [43], kriptografi [25], [26], blockchain [63], dan pengajaran komputasi kuantum untuk remaja [20]. Beberapa sitasi juga tidak cocok dengan kalimatnya; misalnya algoritma *First Byte* dirujuk ke [57], yang membahas optimasi jaringan listrik.");
P("Draf baru mempertahankan 15 entri proposal yang lengkap dan relevan: Kumar 2022, Sharma 2024, Rathore 2025, Osaba 2022, Chiew 2024, Ravish 2024, Du 2022, Zhou 2023, Hessen 2023, Gong 2015, Zhang 2023, Wu 2020, Akin 2019, Al-Saadi 2023, dan Xiang 2022. Dua entri yang metadatanya rusak dipulihkan setelah diverifikasi, yaitu Yang dkk. 2023 (*IEEE Commun. Surveys Tuts.*) dan Rajak dkk. 2023 (*Phil. Trans. R. Soc. A*). Entri lainnya berasal dari artikel IJIES, BAB V, dan BAB VI, ditambah lima rujukan baku yang sudah diverifikasi (Mnih 2015 untuk DQN, Dorigo 2006 untuk ACO, Katoch 2021 untuk GA, Fisher 1981 untuk relaksasi Lagrangian, dan RFC 2474 untuk DiffServ), sehingga daftar pustaka berisi 64 entri yang semuanya dikutip.");

H2("4. BAB IV");
H3("4.1 Posisi BAB IV terhadap BAB V–VI");
P("BAB IV memakai masalah yang berbeda (penempatan flow ke server, kapasitas per node 100/80/60/50 Mbps, 1.600 variabel x_{f,s}) dari BAB V–VI (admisi flow dan jalur, 96 arc berarah 50 Mbps). Bobotnya juga berbeda: λ = (10, 5, 3, 2, 1), dengan urutan *latency* 5 dan *balance* 2, sedangkan di BAB V *balance* 5 dan *latency* 3. Lingkungannya pun berbeda: OpenJij 0.5.x dan Python 3.10 di Colab, sedangkan BAB V–VI memakai OpenJij 0.12.2 dan Python 3.13. Perbedaan ini sah selama BAB IV diposisikan sebagai studi eksploratif, dan draf BAB III menjelaskannya pada Subbab 3.3.5 serta Tabel 3.4. Klaim kesimpulan BAB IV perlu disesuaikan agar tidak bertentangan dengan BAB V.");
H3("4.2 Masalah yang Perlu Diperbaiki");
TABLE("Temuan pada BAB IV dan saran perbaikan", ["Lokasi", "Masalah", "Saran"], [
  ["4.1; 4.4; Tabel 4.4", "Tujuan “membuktikan SQA lebih optimal … latency prioritas utama”, tetapi ACO memberi latency terendah; SQA dinyatakan “#1 Overall” tanpa aturan pemeringkatan", "ubah menjadi tujuan eksploratif; hapus “#1 Overall” atau definisikan aturan agregasi (mis. peringkat rata-rata)"],
  ["4.2.4; 4.3.2.1", "H_latency (λ = 5) disebut “bobot tertinggi/terbesar”, padahal H_constraint λ = 10", "tulis “bobot tertinggi di antara suku objektif (di luar kendala)”"],
  ["4.2.2; 4.2.3; 4.3.5", "permintaan flow hingga 80 Mbps melebihi kapasitas host 50 Mbps; total permintaan tidak disebut", "nyatakan D_{tot} dan kapasitas total (16 × 50 = 800 Mbps); jelaskan perlakuan flow > 50 Mbps"],
  ["4.3.1", "definisi *packet loss* (40% = 40 dari 100 flow?) dan *throughput* tidak diberikan", "tambahkan definisi operasional (kini ada di BAB III Subbab 3.6)"],
  ["Tabel 4.3", "huruf tebal dipakai untuk nilai terbaik dan terburuk (DQN latency 3,8470; ACO loss 44,00)", "samakan dengan keterangan warna atau pakai satu penanda"],
  ["4.3.2.3", "“SQA yang unggul dalam latency” bertentangan dengan Tabel 4.3; “rela mengalihkan … meskipun over-capacity” menunjukkan solusi tak layak ikut dinilai", "koreksi kalimat; nyatakan bahwa tidak ada *repair* kelayakan"],
  ["4.3.3; 4.3.8.1; 4.4", "seluruh 100 *reads* berenergi sama (−837,5675) dijadikan bukti *quantum tunneling*", "energi sama menunjukkan sampler konvergen ke keadaan yang sama, bukan bukti *tunneling*; SQA adalah simulasi CPU (lihat BAB V)"],
  ["4.3.6", "waktu SQA 449,46 s vs GA 4,05 s; kualitas dibandingkan tanpa anggaran setara; panel skalabilitas tanpa metode", "nyatakan sebagai keterbatasan; jelaskan N dan seed pada panel skalabilitas"],
  ["4.3.7", "merujuk “Gambar 4.10” yang tidak ada; menyatakan SQA rata-rata terbaik untuk latency, bertentangan dengan hasil satu seed; tanpa angka dan uji", "ganti menjadi Gambar 4.9; sajikan tabel rata-rata ± SD lima seed; nyatakan analisis deskriptif"],
  ["4.3.8.2", "klaim waktu “sub-second” pada QPU D-Wave tanpa rujukan", "hapus atau beri rujukan dan nyatakan sebagai dugaan"],
  ["4.3.8; Tabel 4.2", "DQN berhenti pada ε = 0,222 (belum konvergen)", "nyatakan sebagai keterbatasan pembanding"],
  ["seluruh bab", "tidak ada sitasi dan daftar pustaka", "tambahkan sitasi IEEE untuk OpenJij, DQN, ACO, GA, JFI, RFC 2474 (nomor dari daftar pustaka BAB I–III)"],
  ["Tabel 4.1", "“Seed 42 (seluruh metode)” padahal analisis multi-seed memakai 5 seed", "tulis “42 (utama); 42, 123, 456, 789, 1234”"],
], [2.6, 6.4, 6.0], null, { size: 18 });

H2("5. BAB V");
H3("5.1 Rujukan Silang ke BAB III");
P("BAB V merujuk ke BAB III di delapan tempat, ditambah satu rujukan ke “butir ii” eksperimen lanjutan. Draf BAB III disusun agar semua rujukan tersebut tepat sasaran tanpa mengubah BAB V:");
TABLE("Rujukan BAB V ke BAB III dan pemenuhannya di draf", ["Rujukan di BAB V", "Isi yang dimaksud", "Di draf BAB III"], [
  ["Subbab 3.3 (5.3; dua kali)", "bobot baseline; μ = 20 pada diagonal admisi", "3.3.3 dan 3.3.4"],
  ["Subbab 3.4 (5.3)", "aturan urutan pada langkah *repair*", "3.4.1"],
  ["Subbab 3.7 (5.3; 5.10.2)", "famili (iv) koreksi Bonferroni", "3.7, Tabel 3.8"],
  ["Subbab 3.8 (5.7; 5.9; 5.10.4)", "penskalaan demand instans kecil; pemeriksaan k = 6", "3.8 dan butir (i)"],
  ["“paragraf eksperimen lanjutan metode (butir ii)” (5.3)", "penalti prioritas lunak", "3.8 butir (ii)"],
], [5.0, 5.0, 5.0]);
H3("5.2 Temuan Lain pada BAB V");
UL([
  "**Gaya sitasi.** BAB V memakai nama–tahun dengan “et al.” (mis. “Ye et al., 2024”), sedangkan disertasi akan memakai IEEE bernomor. Ketujuh sitasi perlu diganti dengan nomor dari daftar pustaka gabungan.",
  "**Pustaka belum lengkap.** Entri Yarkoni dkk. (2022) masih bertanda “[volume dan nomor artikel perlu diverifikasi]”; nilai yang benar adalah vol. 85, Art. no. 104001. Entri Santoro dkk. (2002) dan Kadowaki & Nishimori (1998) belum memiliki DOI.",
  "**Pemisah desimal.** Tabel memakai titik (27.5; 0.773), sedangkan teks memakai koma (27,5). Sesuai kaidah bahasa Indonesia, gunakan koma di tabel juga.",
  "**Label berbahasa Inggris pada tabel**, misalnya “SA-mono (default schedule) + repair”, “Greedy-only (repair, no solver)”, dan “initial settings” pada Tabel 5.4. Sebaiknya diterjemahkan atau diberi keterangan.",
  "**Kata ganti tidak seragam**: “kami” (5.3, 5.10.2), “Peneliti” (5.3), dan kalimat pasif. Pilih satu, misalnya kalimat pasif atau “peneliti”.",
  "**Istilah**: BAB V memakai “anil”/“anil kuantum” dan “penerimaan aliran”, sedangkan BAB VI dan draf BAB I–III memakai *annealing* dan “admisi flow”. Judul BAB V juga menulis “Simulasi Kuantum versus Simulasi Annealing”, yang lebih tepat ditulis “*Simulated Quantum Annealing* versus *Simulated Annealing*”.",
  "**Format**: beberapa judul butir di 5.3 rusak karena huruf tebal terpecah (mis. “D****ekomposisi”).",
  "**Konsistensi dengan artikel**: teks artikel IJIES menyebut kandidat jadwal SA β ∈ [5, 14], tetapi data dan gambar penyetelan memakai β ∈ [1, 10]. Draf BAB III mengikuti data ([1; 10]); teks artikel sebaiknya dikoreksi.",
]);
P("Angka-angka utama BAB V (Tabel 5.1–5.8 dan teks) konsisten satu sama lain dan dengan artikel IJIES. Draf BAB I–III mengutip angka tersebut apa adanya.");

H2("6. BAB VI");
UL([
  "Isi BAB VI identik dengan naskah yang disusun sebelumnya dan konsisten dengan BAB V (protokol, seed, dan angka acuan MAS-QA-v2).",
  "Gaya sitasi nama–tahun dengan “dkk.” perlu dikonversi ke IEEE bernomor seperti BAB I–III; 21 entrinya sudah termasuk dalam daftar pustaka gabungan.",
  "Daftar isi proposal memuat judul dan subbab BAB VI versi lama; gunakan judul BAB VI saat ini.",
]);

H2("7. Yang Dilakukan Draf BAB I–III");
UL([
  "Mengikuti struktur proposal: BAB I (1.1–1.6, ditambah 1.7 Sistematika), BAB II (SDN, MAS, *Load Balancing*, *Quantum Computing* untuk LB, *Quantum Annealing*, Studi Pendahulu dan Gap), dan BAB III (Waktu dan Lokasi, Bahan dan Alat, Variabel, Metode Analisis, Diagram Alir, *Fishbone*, Integrasi QA ke SDN dan MAS).",
  "Menambahkan bagian yang diperlukan BAB IV–VI: Fat-Tree dan ECMP, admisi flow dan DiffServ, QUBO dan penalti, SQA dan SA, metode pembanding (ACO, GA, DQN, IP), dekomposisi dan relaksasi Lagrangian, metrik dan uji statistik, serta formulasi dan protokol lengkap.",
  "Menomori BAB III sehingga Subbab 3.3, 3.4, 3.7, dan 3.8 berisi tepat apa yang dirujuk BAB V.",
  "Menulis ulang permasalahan, tujuan, dan keaslian penelitian agar sesuai dengan temuan BAB IV–VI, termasuk temuan negatif dan batas klaim.",
  "Memakai sitasi IEEE bernomor menurut urutan kemunculan, dengan satu daftar pustaka berisi 64 entri.",
  "Menyisakan satu isian: waktu penelitian pada Subbab 3.1.",
]);

H2("8. Prioritas Tindak Lanjut");
OL([
  "Isi waktu penelitian pada Subbab 3.1 dan tinjau draf BAB I–III bersama promotor.",
  "Revisi klaim BAB IV sesuai Tabel A.3, terutama “#1 Overall”, bukti *quantum tunneling*, klaim D-Wave, dan rujukan Gambar 4.10.",
  "Konversi sitasi BAB V dan BAB VI ke IEEE dengan nomor dari daftar pustaka gabungan, dan lengkapi entri Yarkoni.",
  "Seragamkan pemisah desimal, istilah (*annealing*, admisi flow), dan kata ganti di BAB V.",
  "Tulis ulang abstrak dan daftar isi setelah BAB VII selesai.",
]);

D.save(process.argv[2] || "Analisis.docx", "Catatan Analisis");
