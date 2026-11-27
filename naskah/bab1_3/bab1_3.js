// Draf BAB I-III disertasi (gaya sitasi IEEE). Pemakaian: node bab1_3.js <keluaran.docx>
const path = require("path");
const { makeDoc } = require("./lib_bab");
const REFDB = require("./refs_ieee");
const FIG = path.join(__dirname, "..", "..", "figures", "bab1_3");
const D = makeDoc(FIG, REFDB);
const { P, PN, H2, H3, OL, UL, TABLE, FIGURE, EQ, TITLE, REFS } = D;

// =====================================================================================  BAB I
TITLE("I", "PENDAHULUAN", "1", true);

H2("1.1 Latar Belakang");
P("Perkembangan teknologi jaringan komputer dalam dua dekade terakhir ditandai oleh munculnya arsitektur *Software Defined Networking* (SDN). SDN memisahkan bidang kendali (*control plane*) dari bidang data (*data plane*), sehingga keputusan penerusan trafik dapat diatur secara terpusat melalui pengendali (*controller*) yang dapat diprogram @[kreutz2015,nunes2014]. Dengan pandangan global atas topologi dan beban tautan, SDN menjadi platform yang sesuai untuk menerapkan algoritma optimasi, termasuk penyeimbangan beban (*load balancing*) @[gong2015,hamdan2021].");
P("*Load balancing* adalah teknik untuk mendistribusikan trafik ke berbagai server atau jalur agar *throughput* meningkat, *latency* turun, dan tidak terjadi *overload* pada satu sumber daya @[hamdan2021,kumar2022]. Algoritma konvensional seperti *Round Robin*, *Least Connections*, dan *Weighted Fair Queuing* efektif pada banyak skenario, tetapi bersifat statis atau hanya memakai informasi lokal @[akin2019,zhou2023]. Pada jaringan pusat data, masalah ini tampak jelas. Topologi Fat-Tree menyediakan banyak jalur berbiaya sama antara dua host @[alfares2008], tetapi aturan penerusan yang paling banyak dipakai, yaitu *equal-cost multi-path* (ECMP), memilih jalur dengan fungsi hash dan tidak memperhatikan kapasitas tautan @[hopps2000]. Dua flow besar yang di-hash ke tautan yang sama akan saling berebut kapasitas meskipun jalur lain masih longgar, dan flow yang melintasi tautan yang kelebihan beban akan kehilangan paket. Sistem penjadwalan flow terpusat seperti Hedera memanfaatkan pandangan global SDN untuk memindahkan flow besar ke jalur yang lebih longgar, tetapi tidak menolak flow ketika jaringan sudah jenuh @[hedera2010].");
P("Untuk mengatasi keterbatasan tersebut, berbagai pendekatan kecerdasan buatan telah diusulkan. Pembelajaran mesin dan pembelajaran penguatan mendalam (*deep reinforcement learning*, DRL) dipakai untuk memprediksi trafik, memilih jalur, dan menyeimbangkan beban antar-pengendali @[faezi2023,sharma2024,xiang2022,zhang2023mp,wu2020]. Pendekatan DRL juga diterapkan pada optimasi QoS dan rekayasa trafik @[xia2022,ye2023]. Pendekatan ini adaptif terhadap kondisi yang berubah, tetapi memerlukan tahap pelatihan, kualitasnya bergantung pada konvergensi, dan hasilnya sulit direproduksi tanpa kode serta data yang sama @[ye2024].");
P("Selain SDN, sistem jaringan modern juga mengadopsi pendekatan *multi-agent system* (MAS), di mana beberapa agen otonom mengambil keputusan secara lokal tetapi tetap terkoordinasi secara global @[hessen2023]. Varian multi-agen dari pembelajaran penguatan telah dipakai untuk perutean yang tahan terhadap perubahan dan perutean lintas domain pada SDN @[bhavanasi2023,ye2024]. Dalam konteks penyeimbangan beban, pembagian masalah kepada beberapa agen menurunkan ukuran masalah yang harus diselesaikan setiap agen, tetapi menimbulkan pertanyaan tentang bagaimana keputusan para agen dikoordinasikan pada sumber daya yang dipakai bersama.");
P("Salah satu pendekatan yang menjanjikan untuk masalah optimasi kombinatorial seperti ini adalah *quantum annealing*. Metode ini mencari konfigurasi berenergi minimum dari suatu fungsi energi dengan mengevolusikan sistem dari medan transversal menuju Hamiltonian masalah @[kadowaki1998,rajak2023]. Masalah optimasi terlebih dahulu dirumuskan sebagai *quadratic unconstrained binary optimization* (QUBO) atau model Ising @[lucas2014,glover2022]. Berbeda dengan DRL, *quantum annealing* tidak memerlukan data pelatihan karena langsung bekerja pada formulasi matematis masalah. Komputasi kuantum dipandang menjanjikan untuk aplikasi industri dan telekomunikasi @[yarkoni2022,yang2023,phillipson2023], termasuk perutean @[osaba2022,chiew2024] dan penyeimbangan beban pada komputasi berkinerja tinggi @[rathore2025]. Formulasi QUBO dan *annealing* juga telah diterapkan pada perutean jaringan sensor nirkabel, penempatan fungsi jaringan virtual, pemanfaatan bandwidth, perutean dan penetapan panjang gelombang, serta alokasi sumber daya jaringan optik @[chen2022,chiavassa2022,tsai2023,seker2024,witt2024]. Karena perangkat keras kuantum masih terbatas, *simulated quantum annealing* (SQA), yaitu simulasi klasik berbasis Monte Carlo integral lintasan, banyak dipakai sebagai proksi @[martonak2002,santoro2002]. Pembanding klasiknya adalah *simulated annealing* (SA) pada QUBO yang sama @[kirkpatrick1983]. Secara teoretis SQA dapat jauh lebih cepat daripada SA pada kelas instans tertentu @[crosson2016], tetapi hasil itu tidak otomatis berlaku pada instans praktis.");
P("Meski demikian, perbandingan antara pemecah terinspirasi kuantum dan pemecah klasik tidak selalu dirancang untuk memisahkan pengaruh pemecah dari pengaruh hal-hal di sekitarnya. Kinerja *annealer* sangat bergantung pada pengaturan, *embedding*, dan anggaran sampel @[king2023,vert2024]. Paling tidak ada empat faktor yang dapat menjelaskan selisih antara dua pemecah tanpa melibatkan pemecah itu sendiri: (1) kekuatan pembanding klasik yang kadang tidak disetel; (2) aturan admisi yang menentukan flow mana yang dihitung; (3) anggaran komputasi yang diberikan kepada masing-masing metode; dan (4) langkah perbaikan kelayakan (*repair*) yang mengubah keluaran pemecah menjadi penugasan yang sah. Tanpa pengendalian keempat faktor ini, keunggulan yang dilaporkan belum dapat diatribusikan kepada pemecahnya.");
P("Penelitian disertasi ini menjawab persoalan tersebut secara bertahap. Tahap pertama (BAB IV) adalah studi eksploratif yang merumuskan penempatan 100 flow ke 16 server pada Fat-Tree k = 4 sebagai QUBO berukuran 1.600 variabel, lalu membandingkan SQA dengan *Deep Q-Network* (DQN), *Ant Colony Optimization* (ACO), dan *Genetic Algorithm* (GA). Hasilnya menunjukkan bahwa formulasi QUBO dengan SQA dapat diterapkan dan kompetitif: SQA memberi *throughput* tertinggi (691,24 Mbps), ACO memberi *latency* terendah (1,4655 ms), dan GA memberi *packet loss* terendah (35%) serta indeks keadilan tertinggi (0,9500). Tidak ada metode yang unggul pada semua metrik. Tahap ini juga memperlihatkan keterbatasan rancangan perbandingannya: anggaran komputasi tidak disetarakan (SQA 449,46 detik, GA 4,05 detik), DQN belum konvergen setelah 300 episode, hasil utama berasal dari satu seed, tidak ada langkah *repair* yang sama untuk semua metode, dan tidak ada uji statistik berpasangan.");
P("Tahap kedua (BAB V) karena itu dirancang sebagai studi terkontrol. Masalah dirumuskan ulang sebagai admisi flow dan pemilihan jalur pada 96 arc berarah berkapasitas 50 Mbps, dan keempat faktor di atas dikendalikan: kedua pemecah disetel pada seed validasi yang terpisah dari seed evaluasi, anggaran disetarakan, setiap keluaran dinilai setelah *repair* berurutan prioritas yang sama, dan hasil dilaporkan sebagai selisih berpasangan per seed dengan koreksi Bonferroni. Dengan objektif baseline, SQA yang disetel kehilangan 1,6 dan 2,4 poin persentase (pp) flow lebih sedikit daripada SA yang disetel pada 100 dan 150 flow. Namun, objektif baseline mencapai energi minimum ketika semua flow ditolak; setelah reward admisi μ = 20 ditambahkan, keunggulan tersebut hilang. Langkah *repair* ternyata merupakan faktor terbesar (keluaran tanpa *repair* kehilangan 53–96% flow), kehilangan kelas *Expedited Forwarding* (EF) tetap tinggi (34–53% pada 100–150 flow), dan pemrograman integer eksak masih menerima 4,7–9,0 pp flow lebih banyak.");
P("Tahap ketiga (BAB VI) mengembangkan arsitektur multi-agen MAS-QA, yaitu satu agen per pod sumber yang menyelesaikan QUBO lokal dengan SQA ditambah satu *repair* bersama. Tiga perbaikan diuji: reward admisi yang diturunkan secara analitis untuk menghilangkan bias “tolak semua”, pentahapan prioritas untuk melindungi kelas EF, dan koordinasi harga antar-agen pada arc yang dipakai bersama. Pengaruh alokasi anggaran *annealing* dan posisi pipeline terhadap pemrograman integer eksak juga diuji pada Fat-Tree k = 4, 6, dan 8. Seluruh tahap memakai simulasi klasik pada CPU dan dirancang agar dapat dijalankan pada perangkat komputasi yang terbatas, sehingga disertasi ini tidak mengklaim keunggulan perangkat keras kuantum. Gambar 1.1 merangkum keterkaitan ketiga tahap penelitian.");
FIGURE("gambar1_1_peta_penelitian.png", "Peta jalan penelitian disertasi: tiga tahap penelitian dan temuan yang mendorong tahap berikutnya");

H2("1.2 Permasalahan");
P("Berdasarkan latar belakang tersebut, permasalahan penelitian dirumuskan sebagai berikut.");
OL([
  "*Load balancing* pada SDN berbasis topologi Fat-Tree merupakan masalah optimasi kombinatorial yang harus menyeimbangkan beberapa metrik yang saling bertentangan, yaitu *latency*, *throughput*, *packet loss*, dan keadilan, pada trafik berekor berat (distribusi Pareto) dengan tiga kelas QoS (EF, AF, dan BE). Metode metaheuristik (ACO, GA) dan DRL (DQN) memakai cara pencarian yang berbeda-beda dan masing-masing unggul pada metrik tertentu. Permasalahannya adalah bagaimana masalah tersebut dirumuskan sebagai satu fungsi energi QUBO, dan bagaimana kinerja SQA dibandingkan ketiga metode tersebut pada pengujian eksploratif.",
  "Pada admisi flow dan pemilihan jalur di SDN, keluaran pemecah QUBO dapat melanggar kapasitas tautan sehingga harus diperbaiki sebelum dinilai, dan hasil perbandingan antarpemecah dipengaruhi oleh penyetelan, aturan admisi, anggaran komputasi, serta *repair*. Permasalahannya adalah apakah SQA benar-benar kehilangan lebih sedikit flow daripada SA ketika keempat faktor tersebut disetarakan, seberapa besar kontribusi *repair* dan dekomposisi per pod dibandingkan kontribusi pemecah, dan seberapa jauh hasil heuristik dari optimum eksak.",
  "Arsitektur multi-agen MAS-QA memecah masalah per pod sumber sehingga lebih murah diselesaikan, tetapi temuan tahap kedua menunjukkan tiga kelemahan: objektif baseline cenderung menolak semua flow, kelas EF tidak terlindungi, dan agen pod tidak saling melihat beban pada arc bersama. Permasalahannya adalah bagaimana MAS-QA diperbaiki melalui reward admisi analitis, proteksi prioritas bertahap, koordinasi harga antar-agen, dan alokasi anggaran *annealing*, serta pada ukuran jaringan berapa pipeline tersebut mulai lebih praktis daripada pemrograman integer eksak.",
]);
P("Ketiga permasalahan tersebut diturunkan menjadi pertanyaan penelitian yang lebih rinci pada bab hasil masing-masing, sebagaimana dipetakan pada Tabel 1.1.");
TABLE("Pemetaan permasalahan, pertanyaan penelitian, dan bab", ["Permasalahan", "Pertanyaan penelitian rinci", "Bab", "Metode utama"], [
  ["1 – formulasi dan uji eksploratif", "Kinerja SQA dibanding DQN, ACO, GA pada *latency*, *throughput*, *packet loss*, dan keadilan", "IV", "QUBO 1.600 variabel; SQA (OpenJij); DQN, ACO, GA"],
  ["2 – perbandingan terkontrol", "RQ1: SQA vs SA yang disetel; RQ2: kontribusi *repair* dan dekomposisi; RQ3: jarak dari optimum eksak", "V", "Penyetelan pada seed validasi; anggaran setara; uji-t berpasangan, Wilcoxon, Bonferroni; MILP"],
  ["3 – pengembangan multi-agen", "RQ6.1 reward admisi analitis; RQ6.2 pentahapan prioritas; RQ6.3 koordinasi harga; RQ6.4 alokasi anggaran; RQ6.5 titik silang IP eksak", "VI", "MAS-QA per pod; relaksasi Lagrangian; Lex EF → AF → BE; IP eksak k = 4, 6, 8"],
], [3.4, 5.6, 1.1, 5.4]);

H2("1.3 Tujuan Penelitian");
P("Penelitian ini bertujuan menilai secara terkontrol peran *quantum annealing* dalam penyeimbangan beban dan admisi flow pada SDN, serta mengembangkan arsitektur multi-agen yang memanfaatkan bagian yang terbukti bernilai. Tujuan khususnya adalah sebagai berikut.");
OL([
  "Merumuskan *load balancing* SDN pada Fat-Tree k = 4 sebagai fungsi energi QUBO dan mengevaluasi secara eksploratif kinerja SQA terhadap DQN, ACO, dan GA melalui metrik *latency*, *throughput*, *packet loss*, dan indeks keadilan Jain, termasuk karakteristik konvergensi, distribusi beban, waktu komputasi, dan variasi antarseed.",
  "Mengukur selisih kehilangan flow antara SQA dan SA di bawah protokol yang menyetarakan penyetelan, aturan admisi, *repair*, dan anggaran komputasi; memisahkan kontribusi *repair* dan dekomposisi per pod dari kontribusi pemecah; memeriksa pengaruh fungsi objektif melalui kalibrasi reward admisi; serta mengukur jarak hasil dari optimum eksak dan memverifikasi kehilangan flow pada tingkat paket dengan emulasi Mininet.",
  "Merancang dan menguji reward admisi analitis, pentahapan prioritas EF → AF → BE, koordinasi harga antar-agen dengan aturan keputusan yang ditetapkan sebelum uji, serta alokasi anggaran *annealing* pada MAS-QA, lalu menentukan posisi pipeline terhadap pemrograman integer eksak pada Fat-Tree k = 4, 6, dan 8.",
]);

H2("1.4 Batasan Penelitian");
P("Agar penelitian terfokus dan hasilnya dapat ditafsirkan dengan benar, batasan berikut ditetapkan.");
OL([
  "Penelitian dilakukan sepenuhnya dengan simulasi. Topologi utama adalah Fat-Tree k = 4 (16 host, 96 arc berarah 50 Mbps); Fat-Tree k = 6 dipakai sebagai pemeriksaan skala dan k = 8 hanya pada studi pendahuluan koordinasi harga. Jaringan tradisional, *hybrid*, dan pusat data berskala produksi tidak dikaji.",
  "Agen dalam MAS adalah agen perangkat lunak, satu per pod sumber, yang hanya mengambil keputusan admisi dan pemilihan jalur; aspek keamanan dan kegagalan tautan tidak dikaji.",
  "Trafik bersifat statis per instans: permintaan berdistribusi Pareto (bentuk 2, minimum 2 Mbps), rata-rata sekitar 12,8 Mbps per flow, dengan kelas EF 10%, AF 30%, dan BE 60%. Kandidat jalur dibatasi pada jalur terpendek Fat-Tree.",
  "SQA dan SA dijalankan sebagai simulasi klasik pada CPU dengan pustaka OpenJij; tidak ada pengujian pada perangkat *quantum annealer* sehingga tidak ada klaim keunggulan perangkat keras kuantum.",
  "Metrik utama adalah surogat tingkat flow (kehilangan flow, kehilangan bandwidth, kehilangan per kelas, indeks keadilan, dan *latency* jalur); pemeriksaan tingkat paket terbatas pada emulasi Mininet dengan skala permintaan 0,1 dan tanpa delay propagasi.",
  "Metode berbasis pembelajaran (DQN) hanya dievaluasi pada tahap eksploratif; metode pembelajaran dan *quantum annealing* yang dipublikasikan peneliti lain tidak direproduksi.",
  "Eksperimen tahap kedua dan ketiga dirancang agar dapat dijalankan pada komputer dua inti; waktu dinding diukur pada satu mesin dan bukan tolok ukur pengendali yang diterapkan.",
]);

H2("1.5 Manfaat Penelitian");
P("Secara teoretis, penelitian ini memperluas pemahaman tentang kapan selisih antara SQA dan SA mencerminkan pemecah dan kapan mencerminkan fungsi objektif atau langkah *repair*, termasuk temuan bahwa objektif QUBO yang umum dipakai dapat mencapai energi minimum pada keadaan “tolak semua”. Secara metodologis, penelitian ini menyediakan protokol evaluasi yang dapat dipakai ulang untuk membandingkan pemecah QUBO pada masalah jaringan: seed validasi dan evaluasi yang terpisah, anggaran yang disetarakan, *repair* bersama, uji berpasangan, famili koreksi yang ditetapkan sebelum analisis, dan aturan keputusan yang ditetapkan sebelum uji. Kode, data, dan skrip analisis dirilis agar hasil dapat direproduksi.");
P("Secara praktis, hasil penelitian memberi pedoman bagi perancang pengendali SDN: kapan dekomposisi per pod menghemat kerja komputasi, kapan pentahapan prioritas diperlukan untuk melindungi trafik EF, dan kapan pemrograman integer eksak masih lebih tepat. Perbandingan dengan metode metaheuristik dan DRL pada tahap eksploratif juga memberi gambaran awal bagi praktisi dalam memilih pendekatan optimasi sesuai kebutuhan jaringannya.");

H2("1.6 Keaslian dan Kebaruan Penelitian");
P("Penelitian ini merupakan karya asli yang dirancang dan dilaksanakan sendiri oleh peneliti, mulai dari perumusan QUBO, implementasi pemecah dan koordinator, hingga eksperimen, analisis statistik, dan pelaporan, sehingga bukan merupakan duplikasi dari penelitian pihak lain. Penerapan *quantum annealing* untuk penyeimbangan beban telah dikaji pada domain lain, misalnya komputasi berkinerja tinggi @[rathore2025], dan QUBO telah dipakai untuk berbagai masalah jaringan @[chiavassa2022,tsai2023,seker2024,witt2024]. Kebaruan penelitian ini dirumuskan sesuai bukti pada setiap tahap.");
OL([
  "**Tahap eksploratif (BAB IV).** Kebaruan terletak pada perumusan *load balancing* SDN Fat-Tree sebagai satu fungsi energi QUBO lima komponen (kendala, *latency*, *throughput*, keseimbangan, dan keadilan) dan perbandingannya dengan tiga paradigma lain (DRL, *swarm intelligence*, dan algoritma evolusioner) pada trafik Pareto dengan kelas DiffServ. Tahap ini menunjukkan bahwa tidak ada metode yang unggul pada semua metrik dan mengidentifikasi faktor rancangan yang harus dikendalikan pada tahap berikutnya.",
  "**Tahap terkontrol (BAB V).** Kebaruan terletak pada formulasi QUBO admisi flow dan pemilihan jalur dengan slack biner untuk kapasitas keras dan suku keadilan bandwidth terlayani antar-kelas, serta pada protokol yang mengendalikan empat faktor pengganggu sekaligus. Dengan protokol ini ditunjukkan bahwa keunggulan SQA atas SA merupakan sifat objektif baseline dan aturan *repair*, bukan sifat pemecah, dan bahwa pipeline dekomposisi per pod mencapai kehilangan flow SQA monolitik dalam 0,6 pp dengan sekitar seperenam kerja *annealing*.",
  "**Tahap pengembangan (BAB VI).** Kebaruan terletak pada syarat analitis reward admisi per flow (μ_{f}) yang menghilangkan pencarian μ secara empiris dan memungkinkan penghapusan slack biner pada arc bersama (kerja *annealing* 40–49% dengan kualitas setara), pada pentahapan prioritas leksikografis yang menurunkan kehilangan EF menjadi 2–5% dengan biaya kenaikan kehilangan total 2,5–2,9 pp, dan pada evaluasi terkontrol koordinasi harga antar-agen yang menunjukkan bahwa *repair* bersama sudah berfungsi sebagai koordinator implisit. Temuan negatif ini dilaporkan sebagai batas peran koordinasi dalam arsitektur multi-agen.",
]);

H2("1.7 Sistematika Penulisan");
P("Disertasi ini disusun dalam tujuh bab. BAB I menguraikan latar belakang, permasalahan, tujuan, batasan, manfaat, serta keaslian dan kebaruan penelitian. BAB II menyajikan tinjauan pustaka tentang SDN, MAS, *load balancing*, komputasi kuantum, *quantum annealing*, metode pembanding, metrik dan uji statistik, studi pendahulu, serta kerangka konseptual. BAB III menjelaskan metode penelitian, termasuk model jaringan, formulasi QUBO, koordinator *repair*, pemecah, variabel, metode analisis, dan tahapan penelitian. BAB IV menyajikan hasil studi eksploratif SQA dibandingkan DQN, ACO, dan GA. BAB V menyajikan hasil studi terkontrol SQA dibandingkan SA. BAB VI menyajikan pengembangan arsitektur multi-agen MAS-QA. BAB VII berisi kesimpulan dan saran.");

// =====================================================================================  BAB II
TITLE("II", "TINJAUAN PUSTAKA", "2");

H2("2.1 *Software Defined Networking* (SDN)");
P("*Software Defined Networking* (SDN) adalah paradigma jaringan yang memisahkan lapisan kontrol dari lapisan data yang meneruskan trafik @[kreutz2015,nunes2014]. Pemisahan ini memungkinkan pengaturan jaringan yang lebih fleksibel, karena pengendali SDN yang terpusat dapat mengubah aturan trafik dan kebijakan jaringan melalui perangkat lunak @[gong2015]. Gambar 2.1 memperlihatkan arsitektur SDN dalam tiga lapisan.");
FIGURE("gambar2_1_arsitektur_sdn.png", "Arsitektur SDN tiga lapisan dan antarmuka northbound/southbound", 470);
H3("2.1.1 Karakteristik Utama SDN");
P("Tiga karakteristik utama SDN relevan bagi penelitian ini @[kreutz2015,gong2015]. Pertama, pemisahan lapisan kontrol dan data memungkinkan pengendali terpusat mengatur perangkat penerusan secara dinamis. Kedua, pemrograman tersentralisasi membuat pengendali memiliki pandangan global atas topologi dan beban tautan. Ketiga, agilitas dan fleksibilitas memudahkan penerapan kebijakan baru dan integrasi dengan aplikasi, termasuk modul optimasi seperti yang dikembangkan dalam disertasi ini.");
H3("2.1.2 Komponen SDN");
P("SDN terdiri atas tiga komponen utama @[nunes2014,gong2015]. Pengendali SDN adalah komponen perangkat lunak pusat yang berkomunikasi dengan elemen jaringan untuk mengarahkan trafik dan mengelola tabel penerusan. *Southbound API*, misalnya OpenFlow, adalah protokol komunikasi antara pengendali dan perangkat penerusan, yang dipakai untuk memasang aturan dan mengumpulkan status. *Northbound API* menghubungkan pengendali dengan aplikasi jaringan, sehingga aplikasi seperti penyeimbang beban dapat memanfaatkan visibilitas dan kemampuan kontrol SDN.");
H3("2.1.3 Arsitektur SDN");
P("Arsitektur SDN dapat dijelaskan melalui tiga lapisan fungsional @[kreutz2015]. Lapisan aplikasi berisi aplikasi yang berinteraksi dengan pengendali melalui *northbound API*, misalnya rekayasa trafik, analitik, dan keamanan. Lapisan kontrol berisi pengendali yang memutuskan bagaimana trafik diteruskan. Lapisan infrastruktur berisi *switch* dan *router* yang meneruskan paket sesuai instruksi dari lapisan kontrol. Dalam disertasi ini, modul optimasi MAS-QA ditempatkan pada lapisan aplikasi/kontrol, sedangkan Fat-Tree merupakan lapisan infrastruktur.");
H3("2.1.4 Topologi Pusat Data Fat-Tree dan ECMP");
P("Fat-Tree adalah topologi pusat data berakar ganda yang dibangun dari *switch* komoditas @[alfares2008]. Untuk parameter k, Fat-Tree memiliki k pod, masing-masing berisi k/2 *switch* edge dan k/2 *switch* agregasi, serta (k/2)^{2} *switch* inti dan k^{3}/4 host. Pada k = 4 terdapat 4 pod, 20 *switch*, 16 host, dan 48 tautan fisik. Topologi ini menyediakan beberapa jalur berbiaya sama antar-pod, sehingga muncul pertanyaan jalur mana yang dipilih untuk setiap flow.");
P("ECMP adalah aturan penerusan bawaan pada fabric seperti ini: header paket atau flow di-hash ke salah satu jalur berbiaya sama @[hopps2000]. ECMP tidak memerlukan status dan sangat cepat, tetapi tidak memperhatikan kapasitas tautan, sehingga beberapa flow besar dapat jatuh pada tautan yang sama dan menimbulkan titik panas yang menetap. SDN memungkinkan alternatif yang sadar kapasitas. Hedera, misalnya, memperkirakan permintaan setiap flow, mengidentifikasi flow besar, dan menempatkannya pada jalur yang lebih longgar; bila tidak ada jalur yang cukup, flow tetap memakai jalur hash dan tidak ditolak @[hedera2010]. Karena itu Hedera tidak menjawab pertanyaan flow mana yang harus ditolak ketika fabric sudah jenuh, yang menjadi fokus tahap kedua dan ketiga disertasi ini.");

H2("2.2 *Multi Agent System* (MAS)");
P("*Multi agent system* (MAS) adalah sistem yang terdiri atas sejumlah agen otonom yang berinteraksi dalam lingkungan bersama untuk mencapai tujuan individu maupun kolektif @[hessen2023]. Agen dapat berupa perangkat lunak atau entitas fisik yang mampu mengamati, menalar, berkomunikasi, dan bertindak secara mandiri. MAS memiliki tiga karakteristik utama. Pertama, otonomi: setiap agen mengambil keputusan berdasarkan pengamatan dan tujuan lokalnya. Kedua, desentralisasi: tidak ada satu entitas yang mengendalikan seluruh sistem, sehingga sistem tetap berfungsi bila sebagian agen terganggu dan jumlah agen dapat diperbesar. Ketiga, interaksi dan koordinasi: agen dapat berkolaborasi, bernegosiasi, atau bersaing, baik melalui komunikasi langsung maupun melalui perubahan lingkungan.");
H3("2.2.1 Koordinasi dan Komunikasi Antar Agen");
P("Koordinasi memungkinkan agen menyelaraskan tindakan agar tidak menimbulkan konflik atas sumber daya yang dipakai bersama. Komunikasi antar-agen dapat dilakukan secara langsung (*direct messaging*), yaitu agen bertukar pesan eksplisit berisi status atau permintaan; secara tidak langsung (*stigmergy*), yaitu agen berinteraksi melalui perubahan pada lingkungan; atau secara terstruktur (*protocol-based*), yaitu memakai bahasa komunikasi agen yang baku. Dalam jaringan, koordinasi diperlukan untuk menghindari *bottleneck* dan menjaga keadilan distribusi trafik. Pada MAS-QA, koordinasi dilakukan oleh satu langkah *repair* bersama yang membaca keputusan semua agen pod dan menegakkan kapasitas pada setiap arc (BAB III dan BAB V); koordinasi melalui harga pada arc bersama diuji sebagai alternatif pada BAB VI.");
H3("2.2.2 Penerapan MAS dalam Pengelolaan Trafik dan Distribusi Beban");
P("MAS telah diterapkan untuk distribusi beban pada komputasi awan, di mana agen memantau kondisi server dan mengarahkan permintaan ke server yang lebih longgar @[hessen2023]. Pada SDN, pembelajaran penguatan multi-agen dipakai untuk perutean yang tahan terhadap perubahan topologi dan trafik @[bhavanasi2023] serta untuk perutean lintas domain @[ye2024]. Penerapan lain meliputi pemilihan rute berdasarkan kondisi *delay* dan kemacetan, manajemen bandwidth berdasarkan prioritas layanan, serta deteksi gangguan dan *re-routing*. Integrasi MAS dengan teknik optimasi seperti *quantum annealing* membuka kemungkinan agar setiap agen menyelesaikan subproblem yang lebih kecil, tetapi efektivitasnya bergantung pada cara keputusan para agen dikoordinasikan.");
H3("2.2.3 Dekomposisi dan Koordinasi Berbasis Harga");
P("Masalah optimasi berskala besar dapat dipecah menjadi subproblem per agen bila kendala yang mengikat antar-agen direlaksasi. Relaksasi Lagrangian memindahkan kendala kapasitas bersama g_{l}(x) ≤ c_{l} ke dalam fungsi objektif dengan pengali (harga) π_{l} ≥ 0, sehingga setiap agen dapat menyelesaikan subproblemnya sendiri dengan memperhitungkan harga tersebut @[fisher1981]. Harga diperbarui dengan metode subgradien: harga naik pada sumber daya yang kelebihan beban dan turun pada sumber daya yang longgar.");
EQ("pers2_5.png");
P("Pendekatan dekomposisi yang menghasilkan subproblem QUBO telah dipakai untuk *unit commitment* terdistribusi @[nikmehr2022] dan untuk penjadwalan fungsi jaringan virtual dengan *quantum annealing* paralel berbasis relaksasi Lagrangian @[xuan2024]. Teknik partisi QUBO yang lebih umum juga telah dibahas @[verma2022]. Mekanisme inilah yang diadaptasi pada BAB VI untuk mengoordinasikan agen pod melalui harga pada arc antar-pod.");

H2("2.3 Konsep *Load Balancing*");
P("*Load balancing* bertujuan mendistribusikan beban kerja ke beberapa sumber daya agar pemanfaatan meningkat dan tidak ada sumber daya yang kelebihan beban @[hamdan2021,kumar2022]. Algoritma penyeimbangan beban dapat bersifat statis, yaitu memakai aturan tetap seperti *Round Robin*, atau dinamis, yaitu memakai informasi beban saat itu seperti *Least Connections*. Penyeimbang beban juga dapat berupa perangkat keras khusus atau perangkat lunak; penyeimbang berbasis perangkat lunak lebih fleksibel dan tidak terikat vendor. Pada komputasi awan, metode metaheuristik seperti GA, ACO, dan *particle swarm optimization* telah dibandingkan untuk penjadwalan dan distribusi beban @[zhou2023].");
H3("2.3.1 *Load Balancing* pada SDN");
P("Pada SDN, penyeimbang beban memanfaatkan pandangan global pengendali untuk memilih server atau jalur @[hamdan2021,akin2019]. Pendekatan yang dilaporkan mencakup pemilihan jalur dengan biaya tautan statis dan dinamis @[akin2019], perutean terpisah untuk *elephant flow* dan *mice flow* dengan pembelajaran tak terawasi @[alsaadi2023], serta penyeimbangan beban dengan *deep Q-learning* temporal @[sharma2024]. Kinerja penyeimbangan beban umumnya diukur dengan *throughput*, *delay*, *jitter*, *packet loss*, dan keadilan. *Throughput* adalah jumlah permintaan yang berhasil dilayani, *delay* flow adalah jumlah delay tautan di sepanjang jalurnya, dan *jitter* adalah variasi delay antarpaket yang berurutan.");
EQ("pers2_thr.png");
P("Dalam persamaan tersebut A adalah himpunan flow yang dilayani, d_{f} permintaan flow f, p_{f} jalur flow f, dan d_{e} delay tautan e. Definisi operasional metrik yang dipakai pada setiap tahap penelitian diberikan pada BAB III.");
H3("2.3.2 *Load Balancing* pada MAS");
P("Dalam MAS, penyeimbangan beban merupakan proses distribusi beban kerja secara terkoordinasi antar-agen @[hessen2023]. Setiap agen dapat bertindak sebagai pengamat lokal yang memantau beban server atau tautan tertentu, lalu berkoordinasi dengan agen lain untuk mengalihkan trafik dari sumber daya yang kelebihan beban. Keunggulan utama pendekatan ini adalah desentralisasi dan skalabilitas: keputusan diambil secara lokal sehingga sistem tidak bergantung pada satu titik kontrol. Tantangannya adalah konsistensi global, karena keputusan lokal yang masing-masing layak dapat bersama-sama melampaui kapasitas sumber daya yang dipakai bersama. Pada Fat-Tree, sumber daya bersama tersebut adalah arc antara agregasi dan inti yang dilalui flow antar-pod.");
H3("2.3.3 Admisi Flow dan Kelas Layanan DiffServ");
P("Penyeimbangan beban pada fabric pusat data bekerja pada dua tingkat. Tingkat penerusan memutuskan jalur yang diambil flow, sedangkan tingkat admisi memutuskan apakah flow diterima sama sekali. Aturan jalur yang mengabaikan admisi dapat menempatkan flow pada jalur jenuh sehingga flow tersebut hilang. Ketika permintaan total melebihi kapasitas, admisi menjadi keputusan utama: flow mana yang diterima agar trafik yang dilayani sebesar mungkin tanpa melanggar kapasitas tautan.");
P("Trafik dibedakan menurut kelas layanan *Differentiated Services* (DiffServ) @[nichols1998]. Penelitian ini memakai tiga kelas: *Expedited Forwarding* (EF) untuk trafik berprioritas tertinggi, *Assured Forwarding* (AF), dan *Best Effort* (BE), dengan bobot prioritas 3, 2, dan 1. Admisi yang adil secara agregat belum tentu melindungi kelas EF, sehingga kehilangan per kelas perlu diukur tersendiri.");

H2("2.4 *Quantum Computing* untuk *Load Balancing*");
P("Komputasi kuantum memanfaatkan superposisi dan keterkaitan (*entanglement*) untuk memproses informasi, dan isu-isu pentingnya bagi komputasi dan komunikasi telah disurvei secara luas @[yang2023]. Untuk telekomunikasi, komputasi kuantum dipandang menjanjikan terutama untuk masalah optimasi kombinatorial seperti perutean, penjadwalan, dan alokasi sumber daya @[phillipson2023]. Kajian literatur sistematis menunjukkan bahwa masalah perutean merupakan salah satu kelas masalah yang paling banyak dicoba dengan komputasi kuantum @[osaba2022], dan optimasi multi-objektif untuk perutean jaringan dengan komputer kuantum jangka dekat juga telah dikaji @[chiew2024].");
P("Untuk penyeimbangan beban secara khusus, Rathore dkk. menunjukkan bahwa *quantum annealing* dapat dipakai untuk penyeimbangan beban pada komputasi berkinerja tinggi, seperti *adaptive mesh refinement* dan *smoothed particle hydrodynamics* @[rathore2025]. Pada skenario berbasis grid, *quantum annealing* mengungguli metode klasik sederhana seperti *Round Robin*, meskipun belum melampaui algoritma lanjutan seperti *steepest descent*; pada formulasi partikel yang bersifat multi-objektif, solusinya dilaporkan dominan Pareto terhadap metode klasik. Di bidang jaringan, QUBO dan *annealing* telah diterapkan pada optimasi lalu lintas @[inoue2021], perutean jaringan sensor nirkabel @[chen2022], penempatan fungsi jaringan virtual @[chiavassa2022], pemanfaatan bandwidth @[tsai2023], perutean dan penetapan panjang gelombang dengan proteksi @[seker2024], serta alokasi sumber daya jaringan optik @[witt2024]. Pendekatan kuantum variasional juga dikembangkan untuk pembelajaran terdistribusi @[du2022] dan pembelajaran penguatan @[ravish2024].");
P("Literatur tersebut menunjukkan potensi, tetapi juga keterbatasan yang relevan bagi disertasi ini. Pada studi alokasi sumber daya jaringan optik, pembandingnya adalah solusi eksak CPLEX pada instans tiga simpul, dan *annealer* D-Wave tidak menemukan solusi layak untuk instans tersebut dalam lebih dari 600.000 sampel @[witt2024]. Pada studi lain, *embedding* dan pemilihan parameter mengubah hasil perbandingan secara substansial @[vert2024]. Karena itu, klaim keunggulan pemecah kuantum memerlukan protokol yang menyetarakan pembanding.");

H2("2.5 *Quantum Annealing*");
H3("2.5.1 Konsep Dasar *Quantum Annealing*");
P("*Quantum annealing* adalah metode untuk menyelesaikan masalah optimasi kombinatorial dengan mencari keadaan dasar (*ground state*) dari Hamiltonian masalah @[kadowaki1998,rajak2023]. Prinsipnya berasal dari teorema adiabatik: bila sistem kuantum dievolusikan cukup lambat dari Hamiltonian awal yang keadaan dasarnya mudah disiapkan menuju Hamiltonian masalah, sistem tetap berada pada keadaan dasar. Evolusi dikendalikan oleh fungsi jadwal A(t) yang menurun dan B(t) yang meningkat.");
EQ("pers2_2.png");
P("Suku pertama adalah medan transversal yang menciptakan superposisi semua konfigurasi, sedangkan Hamiltonian masalah Ĥ_{P} biasanya berbentuk model Ising dengan bias lokal h_{i} dan kopling J_{ij}:");
EQ("pers2_ising.png");
P("Keunggulan yang sering dikaitkan dengan *quantum annealing* adalah kemampuan menembus penghalang energi yang tinggi tetapi sempit melalui *quantum tunneling*, sedangkan *simulated annealing* harus melompati penghalang tersebut secara termal @[rajak2023]. Perangkat *quantum annealer* telah mencapai ribuan qubit dan memperlihatkan dinamika kritis kuantum pada kaca spin yang dapat diprogram @[king2023], dan penerapannya pada masalah industri telah ditinjau secara luas @[yarkoni2022]. Namun, keunggulan praktis atas metode klasik bergantung pada struktur masalah, *embedding*, dan anggaran sampel, sehingga harus diuji pada masalah yang bersangkutan @[vert2024].");
H3("2.5.2 Formulasi QUBO dan Penalti Kendala");
P("QUBO adalah masalah meminimalkan fungsi kuadratik atas variabel biner. Model ini ekuivalen dengan model Ising melalui transformasi s_{i} = 2x_{i} − 1, sehingga masalah dalam bentuk QUBO dapat diselesaikan oleh *quantum annealer* maupun pemecah klasik @[lucas2014,glover2022].");
EQ("pers2_1.png");
P("Kendala penugasan dan kapasitas tidak dapat dinyatakan langsung, sehingga ditegakkan melalui suku penalti kuadratik. Kendala pertidaksamaan, seperti kapasitas tautan, biasanya diubah menjadi persamaan dengan variabel slack biner. Pemilihan bobot penalti merupakan masalah yang dikenal luas: bila terlalu kecil, pelanggaran kendala dapat menurunkan energi sehingga pemecah mengembalikan solusi tidak layak; bila terlalu besar, penalti mendominasi objektif sehingga solusi yang berbeda kualitasnya sulit dibedakan @[glover2022,verma2022]. Alternatif tanpa slack biner, seperti *unbalanced penalization*, juga telah diusulkan @[montanez2024]. Karena kelayakan tidak dijamin oleh pemecah, langkah perbaikan (*repair*) diperlukan sebelum solusi dibandingkan.");
H3("2.5.3 *Simulated Quantum Annealing* (SQA)");
P("SQA adalah simulasi klasik dari dinamika *quantum annealing* dengan metode Monte Carlo integral lintasan (*path-integral Monte Carlo*, PIMC) @[martonak2002,santoro2002]. Melalui dekomposisi Suzuki–Trotter, sistem kuantum dengan medan transversal Γ dipetakan menjadi P salinan (irisan Trotter) sistem klasik yang saling terkopel. Setiap irisan memuat energi masalah, dan irisan yang berdekatan dikopel dengan kekuatan J_{⊥} yang membesar saat Γ diturunkan:");
EQ("pers2_4.png");
P("Secara teoretis SQA dapat jauh lebih cepat daripada SA pada kelas instans tertentu @[crosson2016]. Dalam penelitian ini SQA dijalankan dengan pustaka OpenJij @[openjij2026], dengan parameter suhu invers β, medan transversal Γ, dan jumlah irisan Trotter P. Karena SQA adalah simulasi pada CPU, hasilnya tidak dapat dipakai untuk mengklaim keunggulan perangkat keras kuantum.");
H3("2.5.4 *Simulated Annealing* (SA)");
P("SA adalah metode optimasi klasik yang meniru proses pendinginan logam @[kirkpatrick1983]. Pada setiap langkah, satu variabel diubah, dan perubahan diterima menurut kriteria Metropolis:");
EQ("pers2_3.png");
P("ΔE adalah perubahan energi, sedangkan β adalah suhu invers yang dinaikkan menurut jadwal tertentu. Jadwal SA merupakan sumber sensitivitas yang dikenal; pembanding SA dengan jadwal bawaan dapat lebih lemah daripada SA yang disetel, sehingga selisih yang dilaporkan dapat mencerminkan pembanding dan bukan pemecah yang diusulkan @[vert2024]. Karena itu, penelitian ini menyetel jadwal SA secara eksplisit.");
H3("2.5.5 Mesin Ising dan Pemecah Terinspirasi Fisika");
P("Selain *quantum annealer*, berbagai mesin Ising, baik kuantum maupun klasik, dikembangkan sebagai pemecah QUBO @[mohseni2022]. Contohnya adalah *simulated bifurcation* yang memakai mekanika klasik @[goto2021], *digital annealer* @[tsai2023,seker2024], dan jaringan saraf graf yang terinspirasi fisika @[schuetz2022]. Keberagaman ini menegaskan bahwa formulasi QUBO bersifat netral terhadap pemecah, sehingga protokol evaluasi yang adil diperlukan untuk menentukan pemecah mana yang benar-benar bernilai bagi masalah tertentu.");

H2("2.6 Metode Optimasi Pembanding");
H3("2.6.1 *Ant Colony Optimization* (ACO)");
P("ACO meniru perilaku semut yang meninggalkan jejak feromon untuk menemukan jalur terpendek @[dorigo2006]. Setiap semut membangun solusi secara bertahap dengan memilih komponen j dari keadaan i menurut peluang yang sebanding dengan intensitas feromon τ_{ij} dan informasi heuristik η_{ij} (misalnya 1/delay), dengan parameter α dan β. Setelah setiap iterasi, feromon menguap dengan laju ρ dan diperkuat pada komponen solusi yang baik.");
EQ("pers2_aco.png");
P("ACO cepat menemukan solusi yang baik, tetapi dapat konvergen prematur bila feromon terkonsentrasi pada sedikit komponen.");
H3("2.6.2 *Genetic Algorithm* (GA)");
P("GA adalah algoritma evolusioner yang memelihara populasi solusi dan memperbaikinya melalui seleksi, pindah silang (*crossover*), dan mutasi @[katoch2021]. Seleksi turnamen dan elitisme mempertahankan solusi terbaik antar-generasi, sedangkan mutasi menjaga keragaman populasi. GA tidak memerlukan gradien dan mudah menangani fungsi objektif multi-kriteria, tetapi kinerjanya bergantung pada ukuran populasi, jumlah generasi, serta laju pindah silang dan mutasi.");
H3("2.6.3 *Deep Q-Network* (DQN)");
P("DQN adalah metode pembelajaran penguatan yang mendekati fungsi nilai aksi Q(s, a) dengan jaringan saraf dalam @[mnih2015]. Agen memilih aksi dengan strategi ε-greedy, menyimpan pengalaman pada *replay buffer*, dan memperbarui parameter θ dengan meminimalkan galat temporal terhadap jaringan target θ^{−}:");
EQ("pers2_dqn.png");
P("Faktor diskonto γ menentukan bobot imbalan masa depan. DQN mampu belajar dari interaksi dengan lingkungan, tetapi memerlukan banyak episode pelatihan dan sensitif terhadap jadwal eksplorasi; agen yang belum konvergen akan memberi kebijakan yang belum optimal.");
H3("2.6.4 ECMP, Koordinator Greedy, dan Pemrograman Integer Eksak");
P("Selain metaheuristik dan DRL, tiga jenis pembanding dipakai sebagai acuan. ECMP dengan hash merupakan batas bawah tanpa optimasi @[hopps2000], dan varian ECMP dengan admisi sadar kapasitas menerima flow pada jalur hash hanya bila kapasitas masih tersedia. Koordinator greedy menerima flow menurut urutan prioritas pada jalur pertama yang muat. Pemrograman integer (*integer programming*, IP) eksak memberi optimum yang dapat dipakai sebagai acuan; dalam penelitian ini IP diselesaikan dengan pemecah HiGHS melalui SciPy @[virtanen2020]. Tabel 2.1 merangkum karakteristik pemecah yang dibahas.");
TABLE("Karakteristik metode optimasi yang dibahas dan perannya dalam disertasi", ["Metode", "Prinsip", "Pelatihan", "Jaminan kelayakan", "Peran dalam disertasi"], [
  ["SQA", "PIMC atas P irisan Trotter, Γ diturunkan", "tidak", "tidak (perlu *repair*)", "pemecah utama (BAB IV–VI)"],
  ["SA", "Metropolis, β dinaikkan", "tidak", "tidak (perlu *repair*)", "pembanding klasik utama (BAB V)"],
  ["ACO", "feromon dan heuristik 1/delay", "tidak", "bergantung pengodean", "pembanding eksploratif (BAB IV)"],
  ["GA", "seleksi, pindah silang, mutasi", "tidak", "bergantung pengodean", "pembanding eksploratif (BAB IV)"],
  ["DQN", "aproksimasi Q dengan jaringan saraf", "ya", "bergantung pengodean", "pembanding eksploratif (BAB IV)"],
  ["ECMP / ECMP+adm", "hash jalur; admisi sadar kapasitas", "tidak", "ya (dengan admisi)", "acuan bawah (BAB V–VI)"],
  ["IP eksak (HiGHS)", "*branch-and-bound* pada model integer", "tidak", "ya", "acuan optimum (BAB V–VI)"],
], [2.6, 4.4, 1.7, 3.0, 3.9]);

H2("2.7 Metrik Kinerja dan Uji Statistik");
P("Keadilan distribusi beban diukur dengan indeks keadilan Jain (*Jain's fairness index*, JFI), yang bernilai satu bila semua beban sama dan menurun bila beban makin timpang @[jain1984]. Untuk satu vektor beban berlaku JFI = 1/(1 + CoV^{2}), dengan CoV koefisien variasi populasi; identitas ini dipakai sebagai pemeriksaan konsistensi. Karena beberapa metode dievaluasi pada trafik yang sama, perbandingan paling efisien dilakukan secara berpasangan per seed dengan uji-t berpasangan, dilengkapi uji peringkat bertanda Wilcoxon yang tidak mengasumsikan normalitas @[wilcoxon1945]. Bila banyak perbandingan dilakukan sekaligus, peluang hasil signifikan karena kebetulan meningkat, sehingga nilai p dikoreksi dengan metode Bonferroni @[dunn1961]. Pemeriksaan tingkat paket dapat dilakukan dengan emulator Mininet @[lantz2010] dan pembangkit trafik iperf3 @[iperf2023].");

H2("2.8 Studi Pendahulu dan Gap Literatur");
P("Studi pendahulu adalah kumpulan penelitian sebelumnya yang membahas topik serupa. Kajian ini memperlihatkan pendekatan metodologis yang telah dipakai, hasil yang telah ditemukan, dan keterbatasan yang masih tersisa, sehingga penelitian baru dapat membangun di atas pengetahuan yang ada. Gap literatur adalah celah pengetahuan yang belum dijelaskan secara tuntas oleh studi terdahulu, misalnya belum adanya penerapan pada konteks tertentu, kurangnya bukti empiris, atau keterbatasan metodologi. Tabel 2.2 membandingkan penelitian terdahulu yang paling dekat dengan disertasi ini.");
TABLE("Perbandingan penelitian terdahulu", ["No", "Referensi", "Domain dan masalah", "Metode", "Komponen kuantum", "Catatan dan posisi disertasi"], [
  ["1", "Du dkk. (2022) @[du2022]", "pembelajaran mesin kuantum", "pelatihan terdistribusi VQA (QUDIO)", "VQA", "belum diterapkan pada SDN"],
  ["2", "Zhou dkk. (2023) @[zhou2023]", "komputasi awan, penjadwalan VM", "metaheuristik (PSO, ACO, GA)", "tidak ada", "tidak memakai konteks SDN"],
  ["3", "Rathore dkk. (2025) @[rathore2025]", "penyeimbangan beban HPC", "QUBO pada D-Wave", "QA perangkat keras", "domain berbeda; tidak mengkaji admisi flow"],
  ["4", "Ravish dkk. (2024) @[ravish2024]", "RL kuantum pada lingkungan uji", "VQC-DQN, *hybrid* A2C", "VQC", "belum pada topologi SDN"],
  ["5", "Al-Fares dkk. (2010) @[hedera2010]", "penjadwalan flow pusat data", "estimasi permintaan, penempatan flow besar", "tidak ada", "tidak menolak flow saat jenuh; pembanding terdekat adalah ECMP+adm"],
  ["6", "Xiang dkk. (2022) @[xiang2022]", "beban antar-pengendali SDN", "DQN ganda, migrasi *switch*", "tidak ada", "tingkat pengendali, bukan admisi flow"],
  ["7", "Bhavanasi dkk. (2023) @[bhavanasi2023]", "perutean SDN tahan perubahan", "GNN + DRL multi-agen", "tidak ada", "tanpa QUBO; tanpa admisi"],
  ["8", "Witt dkk. (2024) @[witt2024]", "alokasi sumber daya WAN optik", "ILP → QUBO pada D-Wave", "QA perangkat keras", "pembanding eksak tiga simpul; tanpa anggaran setara"],
  ["9", "Vert dkk. (2024) @[vert2024]", "*maximum cardinality matching*", "QA dibanding SA", "QA perangkat keras", "tidak menyetarakan komputasi; memotivasi protokol anggaran setara"],
  ["10", "Tsai dkk. (2023) @[tsai2023]", "asosiasi pengguna 5G O-RAN", "QUBO pada *digital annealer*", "terinspirasi kuantum", "tanpa pembanding klasik pada abstrak"],
  ["11", "Xuan dkk. (2024) @[xuan2024]", "penjadwalan fungsi jaringan virtual", "relaksasi Lagrangian + QA paralel", "QA", "mekanisme terdekat dengan koordinasi harga BAB VI"],
  ["12", "Disertasi ini", "admisi flow dan jalur SDN Fat-Tree", "QUBO + SQA/SA + *repair*; MAS per pod", "SQA (simulasi)", "mengendalikan penyetelan, admisi, anggaran, dan *repair*"],
], [0.8, 3.0, 3.1, 3.1, 2.2, 3.4], null, { size: 18 });
P("Rekomendasi penelitian lanjutan dari studi-studi tersebut memperkuat arah disertasi ini. Studi pelatihan terdistribusi algoritma kuantum variasional menyarankan adaptasi ke lingkungan multi-agen pada perutean dan penyeimbangan beban @[du2022]. Studi metaheuristik pada komputasi awan menyarankan pengujian pada skenario SDN dengan metrik ketimpangan beban @[zhou2023]. Studi *quantum annealing* untuk HPC menyarankan pengujian pada SDN dengan beban dinamis serta kajian *embedding* @[rathore2025]. Studi RL kuantum menyarankan integrasi dengan metaheuristik dan penerapan pada domain waktu nyata seperti SDN @[ravish2024].");
P("Berdasarkan kajian tersebut, celah literatur yang dijawab disertasi ini dirumuskan sebagai berikut.");
OL([
  "**Celah penerapan.** *Quantum annealing* dan QUBO telah dipakai pada banyak masalah jaringan, tetapi belum pada admisi flow dan pemilihan jalur di fabric SDN Fat-Tree dengan kelas DiffServ, baik secara monolitik maupun dengan dekomposisi multi-agen per pod.",
  "**Celah metodologis.** Sejauh yang dapat diperiksa, belum ada studi yang sekaligus menyetarakan empat faktor yang dapat menjelaskan selisih antarpemecah, yaitu kekuatan pembanding klasik, aturan admisi, anggaran komputasi, dan *repair*. Tanpa pengendalian ini, keunggulan yang dilaporkan tidak dapat diatribusikan kepada pemecah.",
  "**Celah objektif dan prioritas.** Pengaruh bentuk fungsi objektif QUBO terhadap keputusan admisi, termasuk kemungkinan energi minimum berada pada keadaan “tolak semua”, serta perlindungan kelas prioritas dalam pipeline berbasis *annealing*, belum dikaji secara terkontrol.",
  "**Celah koordinasi.** Koordinasi berbasis harga antar-subproblem QUBO telah diusulkan @[xuan2024], tetapi belum dievaluasi terhadap kontrol yang memisahkan efek koordinasi dari efek derau sampler dan pengambilan sampel berulang, khususnya bila sudah ada *repair* bersama.",
]);

H2("2.9 Kerangka Konseptual");
P("Gambar 2.2 merangkum kerangka konseptual disertasi. Masalah admisi flow dan pemilihan jalur dirumuskan sebagai QUBO, diselesaikan oleh SQA atau SA secara monolitik atau per pod, diperbaiki oleh koordinator *repair*, lalu dinilai dengan metrik yang sama untuk semua metode. Empat faktor pengganggu dikendalikan agar selisih dapat diatribusikan kepada pemecah (BAB V), dan empat pengembangan diuji pada bagian-bagian pipeline yang terbukti lemah (BAB VI).");
FIGURE("gambar2_1_kerangka_konseptual.png", "Kerangka konseptual penelitian: pipeline, faktor yang dikendalikan, dan pengembangan pada BAB VI");

// =====================================================================================  BAB III
TITLE("III", "METODE PENELITIAN", "3");
P("Penelitian ini bersifat kuantitatif dan eksperimental berbasis simulasi, dengan pendekatan komparatif. Penelitian dilaksanakan dalam tiga tahap yang saling berurutan (Gambar 3.1): tahap eksploratif (BAB IV), tahap terkontrol (BAB V), dan tahap pengembangan multi-agen (BAB VI). Bab ini menjelaskan waktu dan lokasi, bahan dan alat, model dan formulasi, pemecah, variabel, metode analisis, serta prosedur penelitian. Model, pemecah, dan protokol disajikan dalam urutan yang diperlukan untuk menafsirkannya dengan benar. Prinsip yang mendasari tahap kedua dan ketiga adalah bahwa setiap metode dievaluasi pada kondisi yang sama, yaitu trafik, aturan penilaian, aturan admisi, dan anggaran komputasi yang setara, sehingga selisih kinerja dapat diatribusikan kepada metode itu sendiri.");
FIGURE("gambar3_1_alur_penelitian.png", "Alur penelitian dari studi literatur hingga sintesis", 500);

H2("3.1 Waktu dan Lokasi Penelitian");
P("Penelitian dilaksanakan di Laboratorium Robotik Fakultas Teknik dan Ilmu Komputer Universitas Dharmawangsa, Medan, dengan komputasi yang dijalankan pada komputer laboratorium, layanan Google Colaboratory, dan lingkungan komputasi awan dua inti. Penelitian berlangsung sejak [bulan dan tahun mulai] sampai [bulan dan tahun selesai].");

H2("3.2 Bahan dan Alat Penelitian");
H3("3.2.1 Bahan");
P("Penelitian tidak memakai dataset eksternal. Seluruh bahan penelitian dibangkitkan secara sintetis dan dapat direproduksi dari seed, yaitu:");
UL([
  "**Data topologi** — Fat-Tree k = 4, 6, dan 8 dengan kapasitas dan delay tautan sebagaimana dijelaskan pada Subbab 3.3.1.",
  "**Data trafik** — permintaan flow berdistribusi Pareto dengan kelas DiffServ, dibangkitkan per seed (Subbab 3.3.2).",
  "**Manifes seed** — seed validasi (100–104, pemeriksaan 105–114) dan seed evaluasi (42–71; 42–66 untuk studi skala; 42–61 untuk instans kecil), dicatat dalam berkas manifes pada repositori penelitian.",
  "**Data hasil** — nilai per seed setiap metode dan skenario dalam berkas CSV, yang menjadi masukan skrip analisis dan gambar.",
]);
H3("3.2.2 Alat");
P("Pengembangan kode dilakukan pada komputer laboratorium berupa laptop dengan prosesor Intel Core i5, RAM 8 GB, GPU 4 GB, dan sistem operasi Windows 11. Eksperimen dijalankan pada dua lingkungan sebagaimana dirangkum pada Tabel 3.1. Tahap eksploratif memakai Google Colaboratory dengan GPU NVIDIA Tesla T4 karena metode DQN dilatih dengan PyTorch. Tahap kedua dan ketiga dirancang agar dapat dijalankan pada komputer dua inti tanpa GPU.");
TABLE("Lingkungan komputasi dan perangkat lunak per tahap", ["Komponen", "Tahap 1 (BAB IV)", "Tahap 2–3 (BAB V–VI)"], [
  ["Platform", "Google Colaboratory (GPU *runtime*)", "mesin dua inti (Intel Xeon 2,1 GHz, RAM 7 GB)"],
  ["Akselerator", "NVIDIA Tesla T4 (16 GB VRAM, CUDA 12.8)", "tidak ada (CPU saja)"],
  ["Bahasa", "Python 3.10", "Python 3.13"],
  ["Pemecah *annealing*", "OpenJij 0.5.x (SQASampler)", "OpenJij 0.12.2 (SQASampler, SASampler)"],
  ["Pustaka lain", "PyTorch 2.10.0, NetworkX 3.x", "NumPy, pandas, SciPy 1.18.1 (HiGHS), dwave-tabu, numba"],
  ["Emulasi jaringan", "—", "Mininet 2.3.0, iperf3 3.16"],
  ["Seed", "42 (utama); 42, 123, 456, 789, 1234", "validasi 100–104 (cek 105–114); evaluasi 42–71"],
], [3.2, 5.6, 6.2]);

H2("3.3 Model Jaringan, Trafik, dan Formulasi QUBO");
H3("3.3.1 Model Jaringan");
P("Penelitian memakai topologi Fat-Tree k = 4 @[alfares2008] (Gambar 3.2). Jaringan memiliki empat pod, masing-masing dengan dua *switch* edge dan dua *switch* agregasi, empat *switch* inti, dan 16 host (dua per *switch* edge), sehingga terdapat 20 *switch* dan 48 tautan fisik dupleks penuh. Pada tahap kedua dan ketiga, setiap tautan fisik dimodelkan sebagai dua arc berarah berkapasitas c = 50 Mbps, sehingga terdapat 96 kendala kapasitas. Pemodelan per arc penting karena kedua arah tautan membawa trafik yang independen; menghitung tautan sekali akan menyembunyikan kemacetan pada satu arah.");
FIGURE("gambar3_3_topologi.png", "Topologi Fat-Tree k = 4 yang dipakai pada semua eksperimen utama; warna menandai pod");
P("Delay propagasi diambil sekali dari interval per tingkat dengan seed topologi tetap (42) dan dipertahankan sama untuk semua seed evaluasi: host–edge U[1, 3] ms, edge–agregasi U[0,5; 1,5] ms, dan agregasi–inti U[0,1; 0,5] ms, dengan delay yang sama pada kedua arah. Konstanta normalisasi D_{max} = 2(3,0 + 1,5 + 0,5) = 10 ms adalah batas interval delay enam lompatan antar-pod. Kandidat jalur adalah jalur terpendek Fat-Tree: satu jalur untuk host pada *switch* edge yang sama, dua jalur di dalam pod, dan empat jalur antar-pod, diurutkan menurut delay. Pembatasan ini menjaga ukuran QUBO tetap kecil dan sama dengan himpunan jalur yang dipakai ECMP, sehingga semua metode memilih di antara jalur yang sama. Tabel 3.2 merangkum topologi yang dipakai.");
TABLE("Topologi yang dipakai pada tahap kedua dan ketiga", ["Topologi", "Host", "Arc berarah (50 Mbps)", "Jalur antar-pod", "Agen pod", "Flow", "Penggunaan"], [
  ["Fat-Tree k = 4", "16", "96", "4", "4", "50, 100, 150 (S1–S3)", "evaluasi utama BAB V–VI"],
  ["Fat-Tree k = 6", "54", "324", "9", "6", "338 (setara S2)", "pemeriksaan skala BAB V–VI"],
  ["Fat-Tree k = 8", "128", "768", "16", "8", "800 (setara S2)", "studi pendahuluan BAB VI"],
], [2.4, 1.2, 2.2, 1.8, 1.4, 2.8, 3.4]);
H3("3.3.2 Trafik dan Skenario");
P("Eksperimen utama memakai tiga skenario: S1 dengan 50 flow dan permintaan total 640 Mbps, S2 dengan 100 flow dan 1.278,3 Mbps, serta S3 dengan 150 flow dan 1.920 Mbps. Rata-rata permintaan sekitar 12,8 Mbps per flow di setiap skenario, sehingga skenario berbeda dalam jumlah flow yang berebut fabric yang sama, bukan dalam ukuran flow individual. Permintaan mentah berdistribusi Pareto dengan bentuk 2 dan minimum 2 Mbps, lalu diskalakan agar jumlahnya sama dengan total skenario. Distribusi berekor berat dipakai karena trafik pusat data umumnya didominasi sedikit flow besar, dan flow besar inilah yang penempatannya paling menentukan.");
P("Kelas ditetapkan menurut jumlah flow: 10% EF, 30% AF, dan 60% BE, dengan bobot prioritas 3, 2, dan 1. Label kelas adalah permutasi acak dari pola tetap (round(0,1N) flow EF, round(0,3N) flow AF, dan sisanya BE). Host sumber dan tujuan diambil secara seragam tanpa pengembalian, sehingga tidak ada flow ke diri sendiri. Indeks flow menentukan urutan kedatangan yang hanya dipakai sebagai pemecah seri. Trafik dibangkitkan dari satu generator acak dengan seed evaluasi; pemecah memakai seed bilangan yang sama melalui argumen sampler (subproblem pod q memakai seed × 10 + q), sehingga aliran acak trafik dan pemecah terpisah. Tabel 3.3 merangkum skenario yang dipakai.");
TABLE("Skenario trafik", ["Skenario", "Jumlah flow N", "Permintaan total", "Seed", "Tujuan"], [
  ["S1, S2, S3 (k = 4)", "50; 100; 150", "640; 1.278,3; 1.920 Mbps", "42–71 (30 seed)", "perbandingan utama"],
  ["Studi skala (k = 4)", "50; 100; 200; 300", "12,8 · N Mbps (640–3.840 Mbps)", "42–66 (25 seed; 24 untuk N = 300)", "pengaruh ukuran dan beban"],
  ["Instans kecil (k = 4)", "8; 12", "r · 12,8 · N, r ∈ {0,8; 1,6}", "42–61 (20 seed per setting)", "jarak dari optimum eksak"],
  ["Pemeriksaan k = 6", "338", "4.313,5 Mbps", "42–71 (BAB V); 42–51 (BAB VI)", "fabric lebih besar"],
  ["Studi pendahuluan k = 8", "800", "setara S2 per host", "100–102", "koordinasi harga (BAB VI)"],
], [3.2, 2.4, 3.6, 3.4, 2.8]);
P("Studi skala mempertahankan permintaan per flow 12,8 Mbps sehingga jumlah flow dan permintaan total naik bersama pada fabric yang tetap; hasilnya mengukur pengaruh gabungan ukuran masalah dan beban. Pada k = 6, jumlah flow N = 338 (100 × 54/16 = 337,5, dibulatkan ke atas) dan permintaan total 4.313,5 Mbps dipilih agar permintaan per host setara dengan S2 (79,88 dibanding 79,89 Mbps).");
H3("3.3.3 Formulasi QUBO");
P("Formulasi memiliki tiga jenis variabel biner: y_{f} ∈ {0, 1} menyatakan flow f diterima; x_{f,p} ∈ {0, 1} menyatakan flow f memakai kandidat jalur p; dan s_{l,k} ∈ {0, 1}, k = 0, …, K − 1 dengan K = 6, adalah bit slack untuk arc l. Notasi d_{f} menyatakan permintaan flow f, dan b_{l} beban latar pada arc l dari pod lain (nol pada tahap pod). Fungsi objektif total adalah:");
EQ("pers3_1.png");
P("dengan λ = (λ_{A}, λ_{c}, λ_{l}, λ_{t}, λ_{b}, λ_{f}) = (10, 10, 5, 3, 2, 1) sebagai konfigurasi baseline yang ditetapkan sebelum eksperimen. Suku admisi one-hot memastikan flow yang diterima memilih tepat satu jalur:");
EQ("pers3_2.png");
P("Suku kapasitas dengan slack biner, dalam satuan utilisasi, mengubah pertidaksamaan kapasitas menjadi persamaan:");
EQ("pers3_3.png");
P("Suku keseimbangan menghukum variansi utilisasi arc, dengan |E| = 96 arc:");
EQ("pers3_4.png");
P("Suku latensi berbobot prioritas, dengan w_{f} bobot kelas flow f dan D_{p} delay jalur p:");
EQ("pers3_5.png");
P("Suku bandwidth memberi imbalan pada permintaan yang diterima, dengan D_{tot} permintaan total:");
EQ("pers3_6.png");
P("Suku keadilan bandwidth terlayani menghukum perbedaan rasio bandwidth terlayani ρ_{k} antar-kelas, dengan D_{k} permintaan total kelas k:");
EQ("pers3_7.png");
P("Suku one-hot dan kapasitas bersifat penalti lunak sehingga keluaran pemecah dapat melanggarnya. Penelitian ini tidak mengandalkan bobot penalti untuk menghasilkan solusi layak: koordinator pada Subbab 3.4 menegakkan kapasitas keras pada keluaran setiap metode, sehingga bobot penalti memengaruhi kualitas solusi tetapi tidak memengaruhi kelayakan hasil yang dilaporkan. Selain bobot baseline, enam konfigurasi bobot dievaluasi pada seed validasi 100–104 (baseline, *balance-focus*, *equal weights*, *latency-focus*, *no-fairness*, dan *strong-capacity*). Grid ini memilih λ = (10, 20, 5, 3, 2, 1), yang mendefinisikan varian MAS-QA-tuned. Perbandingan utama SQA terhadap SA diulang di bawah keenam set bobot hanya pada S2; pada S1, S3, dan studi skala perbandingan memakai bobot baseline.");
H3("3.3.4 Pemeriksaan Energi dan Kalibrasi Reward Admisi");
P("Sebagai pemeriksaan fungsi energi, satu instans kecil (3 flow, 2 arc) dienumerasi secara lengkap atas seluruh 2^{19} = 524.288 keadaan biner (3 variabel admisi, 4 variabel jalur, dan 12 bit slack). Minimum global adalah keadaan semua flow ditolak dengan energi QUBO bebas offset E = −20,0, yang juga merupakan energi terendah di antara keadaan layak. Pemeriksaan langsung pada S2 (30 seed) memberi hasil serupa: dengan bobot baseline, keadaan “tolak semua” memiliki energi bebas offset rata-rata sekitar −960, lebih rendah daripada sampel SQA mentah (−692). Penyebabnya adalah suku keseimbangan: untuk flow 23,6 Mbps pada jalur enam arc, H_{bal} naik sekitar 1,25 sehingga biayanya λ_{l} · 1,25 ≈ 6,3, sedangkan imbalan bandwidthnya hanya λ_{b} · d_{f}/D_{tot} ≈ 0,04. Energi QUBO karena itu dipakai sebagai besaran verifikasi dan tidak memeringkat metode menurut metrik admisi. Energi dilaporkan sebagai E = H − C, dengan C konstanta hasil ekspansi suku kuadrat; C tidak mengubah urutan keadaan.");
P("Untuk menguji apakah minimum energi dapat digeser ke arah admisi tanpa mengubah kendala, imbalan linear −μ y_{f} ditambahkan pada diagonal variabel admisi setiap flow:");
EQ("pers3_8.png");
P("Nilai μ dipilih pada seed validasi 100–104 (S2) dari {0, 5, 10, 20, 40, 80} berdasarkan rata-rata kehilangan flow setelah *repair* dan apakah sampel memiliki energi lebih rendah daripada keadaan “tolak semua”. Rata-rata kehilangan flow adalah 39,6% (μ = 0), 36,8% (5), 36,2% (10), 35,8% (20), 36,6% (40), dan 36,0% (80). Untuk μ ≥ 10 sampel selalu berenergi lebih rendah daripada keadaan “tolak semua”. Nilai μ* = 20 dipilih sebagai pilihan praktis karena selisih antara μ = 10 sampai 80 berada dalam sebaran antarseed. Bobot baseline tetap menjadi konfigurasi acuan, dan objektif yang dikalibrasi dievaluasi pada seed 42–71 (BAB V). Pada BAB VI, μ yang dipilih secara empiris ini digantikan oleh reward per flow μ_{f} yang diturunkan secara analitis (Subbab 3.4.3).");
H3("3.3.5 Formulasi pada Tahap Eksploratif");
P("Tahap eksploratif (BAB IV) memakai formulasi yang lebih sederhana, yaitu penempatan 100 flow ke 16 server dengan 1.600 variabel biner x_{f,s} dan 25.552 suku QUBO. Fungsi energinya terdiri atas lima komponen: kendala one-hot (λ = 10), *latency* berbobot prioritas (λ = 5), *throughput* atau kelebihan kapasitas (λ = 3), keseimbangan (λ = 2), dan keadilan (λ = 1). Kapasitas dimodelkan pada node (inti 100, agregasi 80, edge 60, dan host 50 Mbps), bukan pada arc berarah. Tabel 3.4 merangkum perbedaan formulasi dan protokol antara tahap eksploratif dan tahap terkontrol, yang menjadi dasar penafsiran hasil BAB IV.");
TABLE("Perbedaan formulasi dan protokol tahap eksploratif dan tahap terkontrol", ["Aspek", "Tahap 1 (BAB IV)", "Tahap 2–3 (BAB V–VI)"], [
  ["Keputusan", "penempatan flow ke server", "admisi flow dan pemilihan jalur"],
  ["Variabel", "1.600 x_{f,s}", "y_{f}, x_{f,p}, slack s_{l,k}"],
  ["Kapasitas", "per node (100/80/60/50 Mbps)", "per arc berarah (96 × 50 Mbps)"],
  ["Suku dan bobot", "5 suku; λ = (10, 5, 3, 2, 1)", "6 suku; λ = (10, 10, 5, 3, 2, 1)"],
  ["*Repair*", "tidak ada *repair* bersama", "koordinator berurutan prioritas untuk semua metode"],
  ["Anggaran", "tidak disetarakan (4 s sampai 449 s)", "disetarakan dalam *spin-update*"],
  ["Seed", "42; lalu 5 seed", "validasi terpisah; 30 seed evaluasi"],
  ["Statistik", "deskriptif (rata-rata ± SD)", "uji berpasangan, Wilcoxon, Bonferroni"],
], [3.0, 5.6, 6.4]);

H2("3.4 Koordinator *Repair* dan Dekomposisi MAS-QA");
H3("3.4.1 Koordinator *Repair*");
P("*Repair* adalah bagian dari setiap metode, bukan pilihan pascapemrosesan. Arc yang kelebihan beban membuang setiap flow yang melintasinya, sehingga keluaran tanpa *repair* tidak memiliki nilai kehilangan yang bermakna. Koordinator karena itu mendefinisikan himpunan layak untuk setiap metode, dan semua metode dibandingkan pada himpunan bersama tersebut. Koordinator bersifat deterministik dan bekerja dalam empat langkah.");
OL([
  "**Dekode.** Flow diterima oleh sampel hanya bila y_{f} = 1, dan jalurnya adalah kandidat berdelay terendah dengan x_{f,p} = 1. Flow dengan y_{f} = 1 tanpa jalur terpilih, atau dengan x_{f,p} = 1 tetapi y_{f} = 0, ditolak.",
  "**Pengurutan.** Flow diurutkan menurut kelas (EF, lalu AF, lalu BE), lalu permintaan yang lebih besar, lalu indeks flow.",
  "**Lintasan 1.** Beban setiap arc dihitung dari semua flow yang diterima pemecah. Flow dikunjungi menurut urutan tersebut; flow yang jalurnya melintasi arc dengan beban di atas c dipindahkan ke kandidat alternatif pertama yang muat, atau ditolak. Flow yang sudah dikunjungi tidak diperiksa ulang.",
  "**Lintasan 2 (pengisian ulang greedy).** Setiap flow yang ditolak pada lintasan 1 atau oleh pemecah dipertimbangkan lagi dalam urutan yang sama dan diterima pada kandidat pertama yang arc-arcnya masih muat.",
]);
P("Karena lintasan 1 ikut menghitung flow berprioritas lebih rendah yang belum dikunjungi, flow berprioritas lebih tinggi dapat tersingkir akibat beban mereka. Perlindungan prioritas karena itu bergantung pada aturan urutan ini, yang dievaluasi pada analisis sensitivitas BAB V.");
H3("3.4.2 Dekomposisi per Pod");
P("Pipeline MAS-QA mengelompokkan flow menurut pod sumber dan menyelesaikan setiap pod sebagai subproblem QUBO tersendiri dengan b_{l} = 0, sehingga satu agen pod tidak melihat trafik pod lain. Keluaran keempat agen digabung dan diteruskan ke koordinator yang sama (Gambar 3.3). Varian iteratif (ITER-SQA-v2-R3) menyelesaikan ulang setiap pod selama tiga putaran dengan beban latar dari pod lain (versi Jacobi).");
FIGURE("gambar3_2_pipeline.png", "Pipeline MAS-QA dan protokol eksperimen tahap kedua");
H3("3.4.3 Pengembangan MAS-QA pada Tahap Ketiga");
P("Tahap ketiga (BAB VI) mempertahankan koordinator di atas dan menambahkan empat perubahan pada agen pod. Rinciannya diberikan pada Subbab 6.2 sampai 6.5; ringkasannya sebagai berikut.");
UL([
  "**Reward admisi analitis μ_{f}.** Untuk setiap flow dihitung perubahan energi akibat menerima flow tersebut pada jalur terbaiknya, lalu μ_{f} ditetapkan sedikit di atas biaya minimum itu (faktor 1 + ε, ε = 0,1), sehingga menerima flow tidak lagi menaikkan energi. Dengan μ_{f}, slack biner pada arc bersama dapat dihapus dari QUBO pod.",
  "**Pembagian arc dan koordinasi harga.** Arc dibagi menjadi arc lokal pod dan arc bersama antar-pod. Kendala kapasitas arc bersama direlaksasi dengan harga π_{l} yang diperbarui secara subgradien, dengan stabilisasi berupa seed sampler tetap, suku proksimal, rata-rata primal, dan langkah adaptif. Koordinasi ini diuji pada studi pendahuluan dengan aturan keputusan yang ditetapkan sebelum uji.",
  "**Pentahapan prioritas leksikografis (Lex).** Kelas diselesaikan berurutan, EF lalu AF lalu BE; setiap tahap hanya memakai kapasitas yang tersisa dari tahap sebelumnya, dan beban tahap sebelumnya dikunci sebagai pengurang kapasitas pada *repair*.",
  "**Alokasi anggaran.** Kerja *annealing* yang sama dibagi menjadi K sampel pendek, K × (500/K) sweep, lalu dipilih sampel yang menerima flow terbanyak setelah *repair*.",
]);

H2("3.5 Pemecah, Penyetelan, dan Metode Pembanding");
H3("3.5.1 Pemecah dan Penyetelan");
P("Kedua pemecah adalah sampler OpenJij (SQASampler dan SASampler) @[openjij2026]. Untuk SQA, jumlah irisan Trotter P = 16, sedangkan suhu invers β dan medan transversal Γ dipilih pada seed validasi 100–104 dan diperiksa pada seed baru 105–114, menghasilkan β = 0,5 dan Γ = 1,0. Untuk SA, jadwal monolitik dipilih dari empat kandidat pada seed validasi yang sama: jadwal bawaan OpenJij, β ∈ [0,1; 3], β ∈ [0,1; 10], dan β ∈ [1; 10]. Jadwal terpilih adalah β ∈ [0,1; 10]. Karena grid penyetelannya kecil, jadwal bawaan OpenJij juga dilaporkan sebagai pembanding SA kedua. Gambar 3.4 memperlihatkan hasil penyetelan; seed evaluasi tidak pernah dipakai untuk memilih pengaturan.");
FIGURE("gambar3_4_penyetelan.png", "Penyetelan pemecah hanya pada seed validasi: (a) grid β × Γ untuk SQA; (b) kandidat jadwal SA; (c) pemeriksaan pengaturan SQA pada seed baru");
H3("3.5.2 Anggaran yang Disetarakan");
P("Kerja *annealing* dihitung dalam *spin-update*:");
EQ("pers3_11.png");
P("dengan n_{var} jumlah variabel QUBO, P jumlah irisan Trotter (P = 1 untuk SA), n_{sweep} jumlah sweep, dan n_{read} jumlah pembacaan. SQA monolitik memakai 10 pembacaan × 5.000 sweep dengan P = 16, SA monolitik yang disetel memakai 10 pembacaan × 80.000 sweep, dan setiap pod SQA memakai 10 pembacaan × 500 sweep dengan P = 16. Dengan hitungan ini anggaran SQA monolitik dan SA sama (10 × 5.000 × 16 = 10 × 80.000 = 8 × 10^{5} *spin-sweep* per variabel), sedangkan keempat pod bersama-sama memakai sekitar seperenam kerja SQA monolitik (rasio 0,16 pada S1–S3).");
H3("3.5.3 Metode Pembanding pada Tahap Terkontrol");
P("Metode pada tahap kedua disusun sebagai tangga, dan setiap anak tangga mengisolasi satu faktor (Tabel 3.5). Dua metode pertama adalah acuan tanpa pengoptimal, koordinator greedy menambahkan logika *repair* tanpa pemecah, varian SA dan SQA monolitik menguji pemecah, dan pipeline beserta varian iteratifnya menguji dekomposisi.");
TABLE("Metode pembanding pada tahap terkontrol (BAB V)", ["Metode", "Keterangan", "Faktor yang diuji"], [
  ["ECMP-hash", "jalur hash tanpa pemeriksaan kapasitas", "acuan bawah"],
  ["ECMP+adm", "jalur hash dengan admisi sadar kapasitas menurut urutan kedatangan", "penempatan vs admisi"],
  ["Greedy-only", "koordinator diterapkan pada penugasan kosong", "*repair* tanpa pemecah"],
  ["SA-mono-mt + *repair*", "SA monolitik disetel (pembanding SA utama)", "pemecah"],
  ["SA-mono-m + *repair*", "SA monolitik dengan jadwal bawaan OpenJij", "sensitivitas jadwal"],
  ["SQA-mono-v2 + *repair*", "SQA monolitik disetel", "pemecah"],
  ["MAS+SA-m", "SA per pod dengan koordinator", "dekomposisi"],
  ["MAS-QA-v2 (diusulkan)", "SQA per pod disetel dengan koordinator", "dekomposisi"],
  ["ITER-SQA-v2-R3", "MAS-QA-v2 dengan tiga putaran beban latar", "iterasi antar-agen"],
  ["IP, tabu, PT", "IP HiGHS (batas 60 s); tabu search (dua protokol); *parallel tempering* 16 replika", "acuan eksak dan sensitivitas"],
  ["Kontrol tanpa *repair*", "MAS-decomp-only, SQA/SA-mono *raw*, SQA-mono-matched", "kontribusi *repair* dan anggaran"],
], [3.8, 7.2, 4.0]);
H3("3.5.4 Metode Pembanding pada Tahap Eksploratif");
P("Pada tahap eksploratif, SQA dibandingkan dengan tiga metode dari paradigma berbeda, yaitu DQN @[mnih2015], ACO @[dorigo2006], dan GA @[katoch2021], dengan parameter pada Tabel 3.6. Metode-metode ini tidak disetarakan anggarannya dan tidak berbagi langkah *repair*, sehingga hasilnya ditafsirkan sebagai perbandingan eksploratif.");
TABLE("Parameter metode pada tahap eksploratif (BAB IV)", ["Metode", "Kategori", "Parameter utama", "Keterangan"], [
  ["SQA", "kuantum (PIMC)", "reads = 100, sweeps = 5.000, Trotter = 16", "QUBO 1.600 variabel, 25.552 suku"],
  ["DQN", "DRL", "300 episode, lr = 0,001, γ = 0,95, ε: 1,0 → 0,22", "jaringan 4 lapis, *replay buffer* 5.000, *batch* 64"],
  ["ACO", "*swarm intelligence*", "30 semut, 150 iterasi, α = 1, β = 2, ρ = 0,1, Q = 100", "η = 1/delay"],
  ["GA", "evolusioner", "populasi 100, 200 generasi, pindah silang 0,8, mutasi 0,05", "turnamen k = 3, elitisme"],
], [1.8, 2.6, 6.0, 4.6]);
H3("3.5.5 Metode pada Tahap Pengembangan");
P("Tahap ketiga membandingkan Greedy-only dan ECMP+adm (acuan bawah), MAS-QA-v2 (acuan utama), MAS-QA-v2 dengan μ = 20, MAS-QA-μ_{f}, MAS-QA-μ_{f}-Lex, konfigurasi K sampel pendek (2 × 250, 4 × 125, 8 × 62 sweep), IP eksak HiGHS dengan batas 60 detik, dan SA monolitik yang disetel dari data tahap kedua. Evaluasi dibagi menjadi tingkat A (k = 4, S1–S3, 30 seed) dan tingkat B (k = 6, 10 seed), sedangkan koordinasi harga diuji pada studi pendahuluan (k = 4, 6, dan 8) sebelum evaluasi akhir (Subbab 6.5).");

H2("3.6 Variabel Penelitian");
P("Variabel penelitian dikelompokkan menjadi variabel bebas, variabel terikat, dan variabel kontrol (Tabel 3.7).");
TABLE("Variabel penelitian", ["Jenis", "Variabel", "Nilai atau satuan"], [
  ["Bebas", "metode (pemecah, dekomposisi, *repair*)", "Tabel 3.5 dan 3.6; Subbab 3.5.5"],
  ["Bebas", "skenario beban dan topologi", "S1–S3; N = 50–300; k = 4, 6, 8"],
  ["Bebas", "fungsi objektif", "6 set bobot λ; μ ∈ {0, 20}; μ_{f}; λ_{p}"],
  ["Bebas", "anggaran *annealing*", "sweep, pembacaan, K × (500/K)"],
  ["Terikat", "kehilangan flow PL_{flow} (metrik utama)", "%"],
  ["Terikat", "kehilangan bandwidth BWL; kehilangan per kelas PL_{EF}, PL_{AF}, PL_{BE}", "%"],
  ["Terikat", "utilitas berbobot prioritas", "% dari permintaan berbobot"],
  ["Terikat", "JFI dan CoV; *latency* rata-rata dan p95", "tanpa satuan, %; ms"],
  ["Terikat", "kerja *annealing* dan waktu per instans", "*spin-update*; detik"],
  ["Terikat (Tahap 1)", "*latency*, *throughput*, *packet loss*, JFI", "ms; Mbps; %; tanpa satuan"],
  ["Kontrol", "trafik, kandidat jalur, delay, *repair*, seed", "identik untuk semua metode per seed"],
], [2.6, 7.6, 4.8]);
P("Metrik utama tahap kedua dan ketiga didefinisikan sebagai berikut. PL_{flow} adalah persentase dari N flow yang tidak diterima, dengan setiap flow yang ditolak dihitung sebagai kehilangan utuh, dan BWL adalah persentase permintaan yang tidak diterima, dengan A himpunan flow yang diterima:");
EQ("pers3_12.png");
P("Kehilangan per kelas adalah persentase flow yang ditolak di dalam setiap kelas. *Latency* adalah rata-rata delay jalur flow yang diterima berbobot prioritas (bobot 3, 2, dan 1), dan *latency* p95 adalah persentil ke-95 per seed. JFI dan CoV dihitung per seed atas 16 host dari permintaan keluar flow yang diterima @[jain1984]; host tanpa beban tetap dihitung dengan beban nol:");
EQ("pers3_13.png");
P("Bila tidak ada flow yang diterima, JFI ditetapkan 0. Objektif QUBO merupakan surogat bagi PL_{flow}, karena energi menghitung penalti dan suku berbobot, bukan kehilangan flow utuh. Pada tahap eksploratif, metrik yang dipakai adalah *latency* rata-rata (ms), *throughput* sebagai jumlah permintaan yang terlayani (Mbps), *packet loss* sebagai persentase flow yang tidak terlayani, dan JFI atas beban 16 server.");

H2("3.7 Metode Analisis dan Uji Statistik");
P("Rancangan tahap kedua dan ketiga bersifat berpasangan. Trafik, himpunan jalur, dan beban latar ditetapkan per seed dan sama untuk semua metode, sehingga setiap perbandingan menghilangkan variansi antarseed yang sama bagi kedua metode. Untuk setiap perbandingan dilaporkan selisih rata-rata d̄ = A − B, interval kepercayaan 95% berbasis distribusi t, dan nilai p uji-t berpasangan dua sisi:");
EQ("pers3_14.png");
P("Untuk perbandingan utama, nilai p uji peringkat bertanda Wilcoxon eksak juga dilaporkan @[wilcoxon1945], dihitung dengan fungsi wilcoxon SciPy 1.18.1 dengan pengaturan bawaan yang membuang selisih nol @[virtanen2020]. Pada analisis tertentu ditambahkan *bootstrap* berpasangan (10.000 pengambilan ulang) dan uji permutasi pembalikan tanda. Koreksi Bonferroni @[dunn1961] diterapkan pada famili uji yang ditetapkan sebelum analisis (Tabel 3.8). Perbandingan di luar famili tersebut, seperti pemeriksaan k = 6, kapasitas heterogen, prioritas, tabu, dan PT, dilaporkan dengan nilai p tanpa koreksi. Tidak ada klaim kesetaraan dalam ±1 pp untuk perbandingan mana pun.");
TABLE("Famili koreksi Bonferroni", ["Famili", "Isi", "m", "Bab"], [
  ["(i)", "perbandingan berpasangan utama S1–S3", "24", "V"],
  ["(ii)", "klaim utama SQA vs SA dengan objektif baseline: tiga skenario utama dan empat ukuran skala", "7", "V"],
  ["(iii)", "pengulangan klaim utama di bawah enam set bobot pada S2", "6", "V"],
  ["(iv)", "analisis putaran kedua per skenario: SQA − SA (baseline), SQA − SA (μ = 20), SA(μ = 20) − SA(baseline), selisih yang sama untuk MAS-QA, MAS-QA − SQA kerja-setara, MAS-QA − SQA 5.000 sweep", "6 per skenario", "V"],
  ["(v)", "kontrol kerja setara dengan pengaturan awal", "3", "V"],
  ["(i) BAB VI", "MAS-QA-μ_{f} dan MAS-QA-v2 (μ = 20) terhadap MAS-QA-v2", "6", "VI"],
  ["(ii) BAB VI", "kehilangan EF dan PL_{flow} Lex terhadap MAS-QA-μ_{f}", "6", "VI"],
  ["(iii) BAB VI", "tiga konfigurasi K sampel terhadap 1 × 500", "9", "VI"],
], [2.0, 9.4, 1.8, 1.4]);
P("Untuk studi pendahuluan koordinasi harga, aturan keputusan ditetapkan sebelum uji: koordinasi dipertahankan hanya bila lebih baik minimal 1 pp daripada kontrol “terbaik dari 2 restart” pada k = 4 dan k = 6, dengan arah yang sama pada minimal 4 dari 5 seed. Pada tahap eksploratif, analisis bersifat deskriptif: rata-rata dan simpangan baku atas lima seed, kurva konvergensi, distribusi energi, *heatmap* utilisasi, dan waktu komputasi.");

H2("3.8 Acuan Eksak pada Instans Kecil dan Eksperimen Lanjutan");
P("Untuk N ∈ {8, 12} dan rasio beban r ∈ {0,8; 1,6}, permintaan total D_{tot} = r · 12,8 · N Mbps dan trafik dibangkitkan seperti pada Subbab 3.3.2 untuk seed 42–61 (20 seed per setting, 80 instans). Acuan eksak adalah program linear integer yang diselesaikan dengan HiGHS melalui fungsi milp SciPy @[virtanen2020]. Variabel biner x_{f,p} memilih paling banyak satu kandidat jalur per flow, dan setiap arc berarah harus memenuhi batas kapasitas 50 Mbps:");
EQ("pers3_10.png");
P("Dua objektif diselesaikan: jumlah flow yang diterima (OPT-count, acuan bagi PL_{flow}) dan permintaan yang diterima (OPT-bw). Model tidak memiliki suku keseimbangan, latensi, maupun keadilan. Skrip berhenti kecuali SciPy melaporkan status optimal dalam batas waktu 120 detik, sehingga setiap nilai acuan adalah solusi optimal. Heuristik dinilai dengan metrik yang sama dan *repair* yang sama: SQA (β = 0,5; Γ = 1,0; P = 16; 10 × 5.000 sweep), SA (β ∈ [0,1; 10]; 10 × 80.000 sweep), dan MAS-QA (10 × 500 sweep per pod). Model IP yang sama juga diselesaikan untuk seluruh 90 instans utama S1–S3 dengan batas 60 detik.");
P("Tiga eksperimen lanjutan memperluas studi di luar fabric k = 4 dan metrik surogat.");
PN("**(i) Fabric yang lebih besar.** Fat-Tree k = 6 dengan 54 host, 162 tautan fisik, dan 324 arc berarah 50 Mbps; pasangan antar-pod memiliki sembilan kandidat jalur. Dipakai N = 338 flow dan D_{tot} = 4.313,5 Mbps (Subbab 3.3.2), dengan SQA monolitik, SA yang disetel, dan pipeline pada pengaturan yang sama.");
PN("**(ii) Penalti prioritas lunak.** Untuk setiap pasangan flow (g pada kelas lebih tinggi, f pada kelas lebih rendah) yang kandidat jalurnya berbagi arc, ditambahkan penalti yang bernilai nol kecuali flow kelas rendah diterima sementara flow kelas tinggi ditolak. Diuji λ_{p} ∈ {0, 20, 100} pada S2 dengan seed 42–71.");
PN("**(iii) Pemeriksaan tingkat paket.** Himpunan flow yang diterima setiap metode pada S2 dipasang pada Mininet 2.3.0 @[lantz2010] dan dialiri UDP dengan iperf3 @[iperf2023] sesuai permintaan setiap flow. Setiap *switch* adalah node Mininet dengan penerusan IP, setiap flow memiliki alamat sendiri sehingga jalurnya berupa rute statis /32, dan tidak dipakai pengendali OpenFlow. Bandwidth tautan 5 Mbps (50 Mbps × 0,1) dan permintaan diskalakan dengan faktor yang sama; setiap metode dijalankan 10 detik pada jaringan baru, tanpa emulasi delay propagasi.");
EQ("pers3_9.png");
P("Persamaan di atas adalah bentuk penalti prioritas lunak pada butir (ii). Penalti ini besar tetapi lunak, sehingga bukan kendala kelayakan eksak. Selain itu, beberapa analisis sensitivitas dijalankan pada S2: varian *repair* yang mengunjungi flow dari prioritas terendah, kapasitas heterogen (arc agregasi–inti diturunkan menjadi 25 Mbps), suku bandwidth berbobot prioritas, serta tabu search dan *parallel tempering* dengan beberapa anggaran.");

H2("3.9 Prosedur dan Tahapan Penelitian");
H3("3.9.1 Diagram Alir Penelitian");
P("Tahapan penelitian mengikuti Gambar 3.1 dan diuraikan sebagai berikut.");
OL([
  "**Studi literatur dan perumusan masalah.** Kajian SDN, Fat-Tree dan ECMP, MAS, *load balancing*, QUBO, *quantum annealing*, SQA, SA, metaheuristik, dan DRL (BAB II), yang menghasilkan permasalahan, tujuan, dan kerangka konseptual.",
  "**Tahap 1 – studi eksploratif.** Merumuskan QUBO penempatan flow ke server, mengimplementasikan SQA, DQN, ACO, dan GA di Google Colaboratory, lalu membandingkan *latency*, *throughput*, *packet loss*, keadilan, konvergensi, distribusi beban, dan waktu komputasi (BAB IV).",
  "**Evaluasi kritis tahap 1.** Mengidentifikasi faktor yang membatasi penafsiran: anggaran yang tidak setara, satu seed utama, tidak ada *repair* bersama, dan tidak ada uji berpasangan.",
  "**Tahap 2 – studi terkontrol.** Merumuskan ulang masalah sebagai admisi flow dan pemilihan jalur, menyetel pemecah pada seed validasi, menyetarakan anggaran, menerapkan *repair* bersama, menjalankan 30 seed evaluasi, studi skala, instans kecil dengan acuan eksak, kalibrasi objektif, k = 6, dan Mininet, lalu menganalisis dengan uji berpasangan dan koreksi Bonferroni (BAB V).",
  "**Tahap 3 – pengembangan multi-agen.** Menurunkan reward admisi analitis, merancang pentahapan prioritas, menguji koordinasi harga pada studi pendahuluan dengan aturan keputusan, menguji alokasi anggaran, dan membandingkan dengan IP eksak pada k = 4, 6, dan 8 (BAB VI).",
  "**Sintesis dan penulisan.** Menafsirkan hasil ketiga tahap, menjawab permasalahan, menetapkan batas klaim, dan merumuskan saran penelitian lanjutan (BAB VII).",
]);
H3("3.9.2 *Fishbone* Diagram");
P("Diagram *fishbone* pada Gambar 3.5 memetakan faktor-faktor yang memengaruhi hasil utama penelitian, yaitu kehilangan flow dan perlindungan kelas EF. Faktor dikelompokkan menjadi enam: objektif QUBO, pemecah, anggaran, *repair*, trafik, dan topologi. Pemetaan ini menjadi dasar rancangan eksperimen: setiap faktor dikendalikan atau divariasikan secara terpisah agar pengaruhnya dapat diidentifikasi.");
FIGURE("gambar3_5_fishbone.png", "Diagram *fishbone* faktor-faktor yang memengaruhi kehilangan flow dan perlindungan kelas EF");
H3("3.9.3 Integrasi *Quantum Annealing* ke SDN dan MAS");
P("Integrasi *quantum annealing* ke dalam arsitektur SDN dan MAS dilakukan dengan menempatkan MAS-QA sebagai modul optimasi pada lapisan aplikasi/kontrol SDN (Gambar 3.6). Pengendali mengumpulkan status jaringan, yaitu permintaan flow, kelas layanan, topologi, dan kapasitas arc. Flow dikelompokkan menurut pod sumber, dan setiap agen pod membangun serta menyelesaikan QUBO lokalnya dengan SQA; karena subproblem saling independen, agen dapat dijalankan paralel. Keputusan semua agen kemudian diteruskan ke *repair* bersama yang menegakkan kapasitas setiap arc dan urutan prioritas, sehingga koordinasi global terjadi pada satu titik yang deterministik. Hasil akhirnya berupa himpunan flow yang diterima beserta jalurnya, yang dipasang sebagai aturan penerusan pada lapisan infrastruktur. Pada penelitian ini, pemasangan aturan diverifikasi dengan rute statis pada emulasi Mininet; integrasi dengan pengendali OpenFlow atau P4 berada di luar cakupan.");
FIGURE("gambar3_6_integrasi.png", "Integrasi MAS-QA ke dalam arsitektur SDN");

REFS();
D.save(process.argv[2] || "BAB_I-III.docx", "BAB I–III");
