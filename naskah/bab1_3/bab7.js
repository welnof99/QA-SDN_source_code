// BAB VII KESIMPULAN DAN SARAN. Dipanggil dari bab1_3.js agar penomoran sitasi IEEE sama dengan BAB I-III.
module.exports = function bab7(D, first = true) {
  const { P, H2, H3, OL, UL, TABLE, TITLE } = D;
  TITLE("VII", "KESIMPULAN DAN SARAN", "7", first);

  H2("7.1 Kesimpulan");
  P("Disertasi ini menilai peran *quantum annealing* dalam penyeimbangan beban dan admisi flow pada SDN berbasis Fat-Tree melalui tiga tahap: studi eksploratif (BAB IV), studi terkontrol (BAB V), dan pengembangan arsitektur multi-agen MAS-QA (BAB VI). Seluruh pemecah dijalankan sebagai simulasi klasik pada CPU. Kesimpulan untuk setiap permasalahan pada Subbab 1.2 adalah sebagai berikut.");

  H3("7.1.1 Formulasi QUBO dan Perbandingan Eksploratif (Permasalahan 1)");
  P("Penyeimbangan beban 100 flow ke 16 server pada Fat-Tree k = 4 dapat dirumuskan sebagai satu fungsi energi QUBO lima komponen dengan 1.600 variabel biner dan diselesaikan dengan SQA. Pada pengujian eksploratif, SQA memberi *throughput* tertinggi (691,24 Mbps), *latency* terbaik kedua (1,4941 ms, setelah ACO 1,4655 ms), *packet loss* 40% (setelah GA 35% dan DQN 36%), dan indeks keadilan terbaik kedua (0,9343, setelah GA 0,9500). Tidak ada metode yang unggul pada semua metrik. SQA juga membutuhkan waktu terlama (449,46 detik, dibanding GA 4,05 detik), sedangkan DQN belum konvergen setelah 300 episode.");
  P("Karena anggaran komputasi tidak disetarakan, hasil utama berasal dari satu seed, tidak ada langkah *repair* yang sama, dan tidak ada uji statistik berpasangan, hasil tahap ini menunjukkan bahwa QUBO dengan SQA dapat diterapkan dan kompetitif, tetapi tidak cukup untuk menyimpulkan keunggulan SQA. Keterbatasan inilah yang mendorong rancangan terkontrol pada tahap kedua.");

  H3("7.1.2 Perbandingan Terkontrol SQA dan SA (Permasalahan 2)");
  P("Untuk admisi flow dan pemilihan jalur pada 96 arc berarah, dengan penyetelan pada seed validasi, anggaran yang disetarakan, *repair* yang sama, dan uji berpasangan pada 30 seed, diperoleh kesimpulan berikut.");
  OL([
    "**Keunggulan SQA bersifat bersyarat.** Dengan objektif baseline, SQA yang disetel kehilangan 1,6 pp (S2) dan 2,4 pp (S3) flow lebih sedikit daripada SA yang disetel, dan 2,5–3,1 pp lebih sedikit pada 100–300 flow di studi skala; kedua selisih utama tetap signifikan setelah koreksi Bonferroni. Pada 50 flow selisihnya tidak signifikan. Namun objektif baseline mencapai energi minimum ketika semua flow ditolak. Setelah reward admisi μ = 20 ditambahkan, SA sama baiknya atau sedikit lebih baik (+1,00; +0,47; dan +0,69 pp untuk SQA), dan tidak ada selisih yang signifikan setelah koreksi. Keunggulan SQA karena itu merupakan sifat objektif baseline dan aturan *repair*, bukan sifat pemecah.",
    "**Langkah *repair* adalah faktor terbesar.** Tanpa *repair*, keluaran pemecah kehilangan 53–96% flow. Dengan *repair*, pemecah menambah 3,5–8,4 pp di atas koordinator greedy tanpa pemecah, dan pipeline mengungguli ECMP dengan admisi sadar kapasitas sebesar 6,9–7,7 pp pada skenario utama.",
    "**Dekomposisi per pod menghemat kerja, bukan waktu.** Pipeline MAS-QA mencapai kehilangan flow SQA monolitik dalam 0,6 pp dengan sekitar seperenam kerja *annealing*, dan pada kerja yang setara keduanya tidak berbeda signifikan (p ≥ 0,19). Pada mesin dua inti, pipeline tidak lebih cepat dalam waktu dinding (1,5 detik dibanding 1,2 detik), dan iterasi dengan beban latar tidak memberi perbaikan signifikan.",
    "**Kelas EF tidak terlindungi.** Pipeline berbasis pemecah kehilangan 34–53% flow EF pada 100–150 flow, dan penalti prioritas lunak tidak menurunkannya.",
    "**Kedekatan dengan optimum hanya pada instans kecil.** Pada 80 instans dengan N = 8 dan 12, SQA yang disetel tidak pernah meleset dari optimum jumlah. Pada 50–150 flow, IP eksak masih menerima 4,7–9,0 pp flow lebih banyak.",
    "**Pemeriksaan tambahan konsisten.** Pada Fat-Tree k = 6, pipeline kehilangan 10,0 pp flow lebih sedikit daripada ECMP dengan admisi dan 0,7 pp lebih banyak daripada SQA monolitik. Emulasi Mininet menunjukkan tidak ada metode admisi yang memiliki flow dengan kehilangan di atas 1%, sedangkan ECMP tanpa admisi hanya mengirim 84,7% beban tawaran.",
  ]);

  H3("7.1.3 Pengembangan Arsitektur Multi-Agen MAS-QA (Permasalahan 3)");
  OL([
    "**Reward admisi analitis μ_{f}** menghilangkan pencarian μ secara empiris dan memungkinkan penghapusan slack biner pada arc bersama, sehingga kualitasnya setara MAS-QA-v2 dengan 40–49% kerja *annealing*. Namun, μ = 20 yang dipilih secara empiris tetap 1,7–1,8 pp lebih baik pada S2 dan S3.",
    "**Pentahapan prioritas leksikografis (Lex)** menurunkan kehilangan EF sebesar 16–52 pp menjadi 2–5%, dengan biaya kenaikan PL_{flow} total 2,5–2,9 pp pada beban tinggi dan kenaikan utilitas berbobot prioritas 5–12 poin.",
    "**Koordinasi harga antar-agen** tidak menambah kualitas di atas *repair* bersama pada Fat-Tree k = 4, 6, dan 8, setelah efek derau sampler dan pemilihan sampel terbaik dikontrol. *Repair* bersama sudah berfungsi sebagai koordinator implisit.",
    "**Alokasi anggaran**: pada k = 4, membagi kerja yang sama menjadi delapan sampel pendek menurunkan PL_{flow} 1,1–2,9 pp, tetapi efek ini hilang pada k = 6.",
    "**Terhadap IP eksak**, titik silang kualitas belum tercapai: IP tetap 4,7–8,9 pp lebih baik pada semua ukuran yang diuji. Yang berubah adalah waktu: waktu IP naik dari 0,06 detik (S1) hingga batas 60 detik (k = 6), sedangkan pipeline tetap 3,6–20 detik secara berurutan dan dapat diparalelkan per pod.",
  ]);

  H3("7.1.4 Kesimpulan Umum");
  P("Secara keseluruhan, nilai MAS-QA terletak pada dekomposisi per pod yang murah dan dapat diparalelkan serta pada proteksi prioritas yang dapat diatur, bukan pada keunggulan kualitas pemecah kuantum maupun koordinasi antar-agen. Selisih antara SQA dan SA lebih kecil daripada pengaruh fungsi objektif dan langkah *repair*, sehingga evaluasi pemecah QUBO untuk masalah jaringan harus menyetarakan penyetelan, aturan admisi, anggaran, dan *repair* sebelum keunggulan pemecah diklaim. Karena semua pemecah dijalankan sebagai simulasi pada CPU, disertasi ini tidak mengklaim keunggulan perangkat keras kuantum. Tabel 7.1 merangkum jawaban setiap permasalahan.");
  TABLE("Ringkasan jawaban permasalahan penelitian", ["Permasalahan", "Jawaban", "Batas klaim"], [
    ["1 – formulasi dan uji eksploratif (BAB IV)", "QUBO + SQA dapat diterapkan dan kompetitif; tidak ada metode yang unggul pada semua metrik", "anggaran tidak setara, satu seed utama, tanpa *repair* dan uji berpasangan"],
    ["2 – perbandingan terkontrol (BAB V)", "SQA lebih baik 1,6–2,4 pp hanya dengan objektif baseline; *repair* dominan; dekomposisi memakai ±1/6 kerja; IP 4,7–9,0 pp lebih baik", "Fat-Tree k = 4 (cek k = 6), trafik statis, metrik surogat, dua pemecah dengan grid penyetelan kecil"],
    ["3 – pengembangan multi-agen (BAB VI)", "μ_{f} dan Lex bermanfaat; koordinasi harga tidak menambah kualitas; delapan sampel pendek membantu pada k = 4; IP masih lebih baik", "k = 8 dan koordinasi harga hanya pada seed validasi; k = 6 dengan 10 seed; batas IP 60 detik"],
  ], [3.6, 6.2, 5.2]);

  H2("7.2 Saran");
  H3("7.2.1 Saran Pengembangan Metode");
  UL([
    "Menjadikan proteksi prioritas sebagai bagian dari rancangan, bukan dari penalti lunak: pentahapan Lex terbukti efektif untuk EF, dan objektif sadar prioritas yang menjaga kehilangan total tetap rendah perlu dikembangkan.",
    "Mengganti slack biner dengan pengodean kendala pertidaksamaan tanpa slack, seperti *unbalanced penalization* @[montanez2024], dan memverifikasi μ_{f} dengan enumerasi lengkap pada instans kecil.",
    "Menguji skema dekomposisi lain yang menghasilkan subproblem QUBO, seperti ADMM @[nikmehr2022] dan relaksasi Lagrangian paralel @[xuan2024], tetapi selalu terhadap kontrol “terbaik dari K restart” agar efek koordinasi tidak tertukar dengan efek pengambilan sampel berulang.",
    "Memakai pipeline sebagai solusi awal (*warm start*) bagi IP eksak, karena IP masih lebih baik kualitasnya tetapi waktunya naik jauh lebih cepat.",
  ]);
  H3("7.2.2 Saran Evaluasi dan Penelitian Lanjutan");
  UL([
    "Menguji topologi yang lebih besar dan trafik yang berubah menurut waktu, termasuk Fat-Tree k = 8 pada seed evaluasi dan kapasitas heterogen.",
    "Menjalankan protokol yang sama pada perangkat *quantum annealer* atau *digital annealer* dengan anggaran yang disetarakan @[king2023,seker2024], serta pada pemecah terinspirasi fisika lain seperti *simulated bifurcation* dan jaringan saraf graf @[goto2021,schuetz2022].",
    "Membandingkan dengan metode pembelajaran penguatan, termasuk varian multi-agen, dengan anggaran pelatihan yang dilaporkan dan disetarakan @[bhavanasi2023,ye2024].",
    "Memperluas pemeriksaan tingkat paket ke pengendali SDN sesungguhnya (misalnya OpenFlow atau P4) dengan delay propagasi, lonjakan trafik, dan umpan balik transport, serta mengukur waktu ketika agen pod dijalankan paralel.",
    "Menambah jumlah seed pada pemeriksaan k = 6 dan memperbesar grid penyetelan kedua pemecah agar daya uji meningkat.",
  ]);
  H3("7.2.3 Saran Praktis bagi Perancang Pengendali SDN");
  UL([
    "Bila jaminan bagi trafik EF menjadi syarat layanan, gunakan pentahapan prioritas (Lex), yang memberi proteksi hampir setara koordinator greedy dengan kehilangan total yang lebih rendah.",
    "Bila jumlah flow yang diterima menjadi prioritas, gunakan MAS-QA dengan reward admisi μ = 20 atau dengan delapan sampel pendek, dengan menyadari bahwa kehilangan EF tetap tinggi.",
    "Bila instans kecil dan waktu keputusan longgar, gunakan pemrograman integer eksak; pipeline multi-agen lebih tepat bila waktu keputusan ketat dan pod dapat diselesaikan paralel.",
    "Dalam setiap evaluasi pemecah, laporkan anggaran, penyetelan pembanding, aturan admisi, dan langkah *repair* yang dipakai, karena keempat faktor ini dapat mengubah peringkat metode.",
  ]);
};
