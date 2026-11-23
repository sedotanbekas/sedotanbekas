# -*- coding: utf-8 -*-
"""
Translations for the profile lab. One dict per language.

* Placeholders in {braces} are filled in by build.py — keep them.
* "en" and "id" share the original bilingual Indonesian/English lab report;
  every other language gets a translated copy (its own language first,
  the Indonesian original underneath in italics).
* After adding new characters to a non-Latin language, re-run
  `python scripts/fonts.py` so the embedded fonts cover them
  (missing glyphs still render, just in the viewer's system font).
"""

LANGS = ["en", "zh", "hi", "es", "ar", "fr", "bn", "pt", "ru", "id"]

# Indonesian original of the lab report (primary for en/id, secondary for the rest)
COA_ID = {
    "cols": ["No.", "Parameter", "Hasil", "Satuan", "Baku Mutu", "Metode", "Ket."],
    "rows": ["Total kontribusi", "Rata-rata harian", "Streak saat ini", "Streak terpanjang", "Puncak harian",
             "Hari tersibuk", "Senyawa dominan", "Kadar kafein*", "Bug lolos uji*"],
    "u": {"contrib": "kontribusi", "perday": "per hari", "days": "hari", "cups": "cangkir/hari", "release": "per rilis"},
    "l_notreg": "tidak diatur", "m_organo": "Organoleptik", "m_pentest": "Pentest mandiri",
    "meta_l": ["No.", "Tanggal", "Halaman"], "page_v": "1 dari 1",
    "info_l": ["Nama sampel", "Kode sampel", "Matriks", "Diterima", "Periode uji", "Sampling"],
    "matrix_v": "Kode, kopi & deadline", "sampling_v": "Komposit 365 hari · GitHub API",
}
COA_EN = {
    "cols": ["", "Parameter", "Result", "Unit", "Limit", "Method", "Remark"],
    "rows": ["Contributions, rolling 365 days", "Daily mean", "Current streak", "Longest streak", "Peak day",
             "Busiest weekday", "Dominant compound (by bytes)", "Caffeine level", "Escaped bugs, self-pentested"],
}
DAYS_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

T = {}

T["en"] = {
    "native": "English", "dir": "ltr", "dec": ",", "months": "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(),
    "date": "{dd} {mon} {y}", "short": "{mon} {dd}", "days": DAYS_ID,
    "fig": "FIG. 01 — SPECIMEN {code} · RECEIVED {date}",
    "taglines": ["builds the LIMS. then tries to break it.", "Next.js · Prisma · MariaDB · Nginx · PM2",
                 "Bangkit Academy 2024 · Mobile Development", "sedotan bekas = a used straw. still sipping."],
    "labels": ["ROLE", "ORIGIN", "ASSAY"],
    "role_v": "Software Engineer · PT Medialab Indonesia",
    "origin_v": "Informatics Eng. · Politeknik Negeri Jakarta",
    "assay_v": "{n} contributions / 365 d · {r} public repos · since {y}",
    "coa_sub": "Certificate of Analysis — specimen: one (1) developer",
    "notes": ["* Parameter belum terakreditasi. / Parameter not accredited.",
              "Hasil uji hanya berlaku untuk sampel yang diuji.",
              "These results relate only to the specimen tested.",
              "LoD = limit of detection · IK = instruksi kerja (in-house).",
              "Dianalisis ulang otomatis tiap hari 00:17 WIB oleh github-actions[bot]."],
    "approved": "Disahkan oleh / Approved by", "sig_title": "Penyelia Teknis · Technical Supervisor",
    "el_mass": "MASS = % OF CODE (BYTES)", "el_assayed": "{n} repos assayed · markup excluded",
    "el_tools": "* SERI ALAT · TOOLING SERIES", "last_assay": "last assay {date} · {time} WIB",
    "ch_sub": "commit activity", "ch_det": "DETECTOR: UV-GIT @ 254 NM",
    "ch_col": "column: {user}/* · window: {n} d · 1 analyst", "ch_x": "retention time →", "ch_y": "intensity",
    "ch_sum": "∑ area ({n} d) = {win} · peaks ≥ 20: {big} · max {max} @ {date}",
    "s_sample": "SAMPLE", "s_last": "LAST SAMPLED",
    "s_desc": ["Laboratory Information Management System for PT Medialab Indonesia's testing lab.",
               "MediaLab Assist: a TypeScript web helper for day-to-day work at Medialab.",
               "Bangkit Academy 2024 capstone (mobile side): tax made easy for Indonesian UMKM.",
               "Sentiment analysis in the browser: text in, mood out."],
    "footer": "sedotan bekas — dipakai sekali, masih berguna · used once, still useful · last assay {date}, {time} WIB",
    "md_caption": "<b><i>sedotan bekas</i></b> (n., Indonesian): a used straw. Already used once, still useful.",
    "md_abs_h": "> abstract",
    "md_abs": ("I build the in-house software behind **PT Medialab Indonesia**'s testing lab, most visibly its **LIMS**\n"
               "(Next.js · Prisma · MariaDB, shipped to Ubuntu with GitHub Actions, PM2 & Nginx). Then I pentest it myself,\n"
               "so the bugs meet me before they meet anyone else. Informatics Engineering graduate of **Politeknik Negeri Jakarta**\n"
               "and a Bangkit Academy 2024 alumnus (Mobile Development)."),
    "md_samples_h": "> samples on the bench",
    "alt_el": "Periodic table of the languages and tools I work with",
    "alt_ch": "Chromatogram of my daily contributions over the last 120 days",
}

T["id"] = {
    "native": "Indonesia", "dir": "ltr", "dec": ",", "months": "Jan Feb Mar Apr Mei Jun Jul Agu Sep Okt Nov Des".split(),
    "date": "{dd} {mon} {y}", "short": "{dd} {mon}", "days": DAYS_ID,
    "fig": "GBR. 01 — SPESIMEN {code} · DITERIMA {date}",
    "taglines": ["membangun LIMS, lalu mencoba membobolnya.", "Next.js · Prisma · MariaDB · Nginx · PM2",
                 "Bangkit Academy 2024 · Mobile Development", "sedotan bekas, tapi masih bisa nyedot."],
    "labels": ["PERAN", "ASAL", "UJI"],
    "role_v": "Software Engineer · PT Medialab Indonesia",
    "origin_v": "Teknik Informatika · Politeknik Negeri Jakarta",
    "assay_v": "{n} kontribusi / 365 hari · {r} repo publik · sejak {y}",
    "coa_sub": "Sertifikat Analisis — spesimen: satu (1) developer",
    "notes": ["* Parameter belum terakreditasi.",
              "Hasil uji hanya berlaku untuk sampel yang diuji.",
              "LoD = batas deteksi · IK = instruksi kerja (in-house).",
              "Dianalisis ulang otomatis tiap hari 00:17 WIB oleh github-actions[bot]."],
    "approved": "Disahkan oleh", "sig_title": "Penyelia Teknis",
    "el_mass": "MASSA = % KODE (BYTE)", "el_assayed": "{n} repo diuji · markup tidak dihitung",
    "el_tools": "* SERI ALAT", "last_assay": "uji terakhir {date} · {time} WIB",
    "ch_sub": "aktivitas commit", "ch_det": "DETEKTOR: UV-GIT @ 254 NM",
    "ch_col": "kolom: {user}/* · jendela: {n} hari · 1 analis", "ch_x": "waktu retensi →", "ch_y": "intensitas",
    "ch_sum": "∑ luas area ({n} hari) = {win} · puncak ≥ 20: {big} · maks {max} @ {date}",
    "s_sample": "SAMPEL", "s_last": "SAMPLING TERAKHIR",
    "s_desc": ["Laboratory Information Management System untuk lab pengujian PT Medialab Indonesia.",
               "MediaLab Assist: web helper TypeScript untuk pekerjaan harian di Medialab.",
               "Capstone Bangkit Academy 2024 (sisi mobile): urusan pajak UMKM jadi gampang.",
               "Analisis sentimen di browser: teks masuk, suasana hati keluar."],
    "footer": "sedotan bekas — dipakai sekali, masih berguna · uji terakhir {date}, {time} WIB",
    "md_caption": "<b><i>sedotan bekas</i></b> (kata benda): sudah pernah dipakai, tapi masih berguna.",
    "md_abs_h": "> abstrak",
    "md_abs": ("Aku membangun software internal untuk lab pengujian **PT Medialab Indonesia**, yang paling kelihatan adalah **LIMS**-nya\n"
               "(Next.js · Prisma · MariaDB, dirilis ke Ubuntu lewat GitHub Actions, PM2 & Nginx). Setelah itu aku pentest sendiri,\n"
               "supaya bug-nya ketemu aku duluan sebelum ketemu orang lain. Lulusan Teknik Informatika **Politeknik Negeri Jakarta**\n"
               "dan alumni Bangkit Academy 2024 (Mobile Development)."),
    "md_samples_h": "> sampel di meja uji",
    "alt_el": "Tabel periodik bahasa pemrograman dan tools yang kupakai",
    "alt_ch": "Kromatogram kontribusi harianku selama 120 hari terakhir",
}

T["zh"] = {
    "native": "简体中文", "dir": "ltr", "dec": ".", "months": [f"{m}月" for m in range(1, 13)],
    "date": "{y}年{m}月{d}日", "short": "{m}月{d}日",
    "days": ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"],
    "fig": "图 01 — 样品 {code} · 收样日期 {date}",
    "taglines": ["亲手打造 LIMS，再亲手攻破它。", "Next.js · Prisma · MariaDB · Nginx · PM2",
                 "Bangkit Academy 2024 · 移动开发", "sedotan bekas：一根用过的吸管，照样能吸。"],
    "labels": ["职位", "学历", "检测"],
    "role_v": "软件工程师 · PT Medialab Indonesia",
    "origin_v": "信息工程 · Politeknik Negeri Jakarta",
    "assay_v": "近 365 天贡献 {n} 次 · 公开仓库 {r} 个 · 始于 {y} 年",
    "coa_sub": "分析证书 — 样品：开发者一（1）名",
    "coa": {
        "cols": ["序号", "检测项目", "结果", "单位", "限值", "方法", "备注"],
        "rows": ["贡献总数", "日均贡献", "当前连续天数", "最长连续天数", "单日峰值", "最忙的星期几",
                 "主要成分（按字节）", "咖啡因含量*", "漏网 bug*"],
        "u": {"contrib": "次", "perday": "次/天", "days": "天", "cups": "杯/天", "release": "个/版本"},
        "l_notreg": "不设限", "m_organo": "感官检验", "m_pentest": "自主渗透测试",
        "meta_l": ["编号", "日期", "页码"], "page_v": "1 / 1",
        "info_l": ["样品名称", "样品编号", "基质", "收样日期", "检测周期", "采样方式"],
        "matrix_v": "代码、咖啡与截止日期", "sampling_v": "365 天混合样 · GitHub API",
    },
    "notes": ["* 该项目未获认可。", "Hasil uji hanya berlaku untuk sampel yang diuji.", "检测结果仅对所测样品有效。",
              "LoD = 检出限 · IK = 内部作业指导书", "每天 00:17（WIB）由 github-actions[bot] 自动重新分析。"],
    "approved": "Disahkan oleh / 批准人", "sig_title": "Penyelia Teknis · 技术主管",
    "el_mass": "质量 = 代码占比（字节）", "el_assayed": "已检测 {n} 个仓库 · 不含标记语言",
    "el_tools": "* SERI ALAT · 工具系列", "last_assay": "最近检测 {date} · {time} WIB",
    "ch_sub": "提交活动", "ch_det": "检测器：UV-GIT @ 254 NM",
    "ch_col": "色谱柱：{user}/* · 窗口：{n} 天 · 分析员 1 名", "ch_x": "保留时间 →", "ch_y": "强度",
    "ch_sum": "∑ 峰面积（{n} 天）= {win} · ≥ 20 的峰：{big} · 最大值 {max} @ {date}",
    "s_sample": "样品", "s_last": "最近采样",
    "s_desc": ["为 PT Medialab Indonesia 检测实验室打造的实验室信息管理系统（LIMS）。",
               "MediaLab Assist：用 TypeScript 编写的日常工作助手网页。",
               "Bangkit Academy 2024 毕业项目（移动端）：让印尼中小微企业轻松报税。",
               "浏览器里的情感分析：输入文字，输出情绪。"],
    "footer": "sedotan bekas — dipakai sekali, masih berguna · 用过一次，依然有用 · 最近检测 {date} {time} WIB",
    "md_caption": "<b><i>sedotan bekas</i></b>（印尼语，名词）：一根用过的吸管。用过一次，依然有用。",
    "md_abs_h": "> 摘要",
    "md_abs": ("我为 **PT Medialab Indonesia** 的检测实验室开发内部软件，其中最核心的是 **LIMS**"
               "（Next.js · Prisma · MariaDB，通过 GitHub Actions、PM2 和 Nginx 部署到 Ubuntu）。"
               "上线之前，我会亲自对它做渗透测试，让漏洞先撞上我，而不是别人。"
               "毕业于 **Politeknik Negeri Jakarta** 信息工程专业，Bangkit Academy 2024 学员（移动开发方向）。"),
    "md_samples_h": "> 检测台上的样品",
    "alt_el": "我所用编程语言与工具的元素周期表", "alt_ch": "近 120 天每日贡献的色谱图",
}

T["hi"] = {
    "native": "हिन्दी", "dir": "ltr", "dec": ".",
    "months": ["जन॰", "फ़र॰", "मार्च", "अप्रैल", "मई", "जून", "जुल॰", "अग॰", "सित॰", "अक्तू॰", "नव॰", "दिस॰"],
    "date": "{d} {mon} {y}", "short": "{d} {mon}",
    "days": ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"],
    "fig": "चित्र 01 — नमूना {code} · प्राप्ति {date}",
    "taglines": ["LIMS बनाता हूँ, फिर उसे तोड़ने की कोशिश करता हूँ।", "Next.js · Prisma · MariaDB · Nginx · PM2",
                 "Bangkit Academy 2024 · मोबाइल डेवलपमेंट", "sedotan bekas: इस्तेमाल हुई स्ट्रॉ, अब भी काम की।"],
    "labels": ["भूमिका", "शिक्षा", "परीक्षण"],
    "role_v": "सॉफ़्टवेयर इंजीनियर · PT Medialab Indonesia",
    "origin_v": "इन्फ़ॉर्मेटिक्स इंजीनियरिंग · Politeknik Negeri Jakarta",
    "assay_v": "365 दिनों में {n} योगदान · {r} सार्वजनिक रिपॉज़िटरी · {y} से",
    "coa_sub": "विश्लेषण प्रमाणपत्र — नमूना: एक (1) डेवलपर",
    "coa": {
        "cols": ["क्र.", "पैरामीटर", "परिणाम", "इकाई", "सीमा", "विधि", "टिप्पणी"],
        "rows": ["कुल योगदान", "दैनिक औसत", "वर्तमान स्ट्रीक", "सबसे लंबी स्ट्रीक", "एक दिन का शिखर", "सबसे व्यस्त वार",
                 "प्रमुख यौगिक (बाइट के आधार पर)", "कैफ़ीन स्तर*", "बचकर निकले बग*"],
        "u": {"contrib": "योगदान", "perday": "प्रति दिन", "days": "दिन", "cups": "कप/दिन", "release": "प्रति रिलीज़"},
        "l_notreg": "विनियमित नहीं", "m_organo": "ऑर्गेनोलेप्टिक", "m_pentest": "स्व-पेनटेस्ट",
        "meta_l": ["क्रमांक", "दिनांक", "पृष्ठ"], "page_v": "1 / 1",
        "info_l": ["नमूने का नाम", "नमूना कोड", "मैट्रिक्स", "प्राप्ति तिथि", "परीक्षण अवधि", "नमूनाकरण"],
        "matrix_v": "कोड, कॉफ़ी और डेडलाइन", "sampling_v": "365-दिवसीय मिश्रित नमूना · GitHub API",
    },
    "notes": ["* यह पैरामीटर मान्यता प्राप्त नहीं है।", "Hasil uji hanya berlaku untuk sampel yang diuji.",
              "ये परिणाम केवल परीक्षण किए गए नमूने पर लागू होते हैं।", "LoD = पहचान सीमा · IK = आंतरिक कार्य निर्देश",
              "github-actions[bot] हर दिन 00:17 WIB पर अपने-आप दोबारा विश्लेषण करता है।"],
    "approved": "Disahkan oleh / अनुमोदक", "sig_title": "Penyelia Teknis · तकनीकी पर्यवेक्षक",
    "el_mass": "द्रव्यमान = कोड का % (बाइट)", "el_assayed": "{n} रिपॉज़िटरी जाँची गईं · मार्कअप शामिल नहीं",
    "el_tools": "* SERI ALAT · टूल श्रृंखला", "last_assay": "अंतिम जाँच {date} · {time} WIB",
    "ch_sub": "कमिट गतिविधि", "ch_det": "डिटेक्टर: UV-GIT @ 254 NM",
    "ch_col": "कॉलम: {user}/* · अवधि: {n} दिन · 1 विश्लेषक", "ch_x": "रिटेंशन टाइम →", "ch_y": "तीव्रता",
    "ch_sum": "∑ क्षेत्रफल ({n} दिन) = {win} · ≥ 20 वाले शिखर: {big} · अधिकतम {max} @ {date}",
    "s_sample": "नमूना", "s_last": "अंतिम नमूना",
    "s_desc": ["PT Medialab Indonesia की परीक्षण प्रयोगशाला के लिए लैबोरेटरी इन्फ़ॉर्मेशन मैनेजमेंट सिस्टम।",
               "MediaLab Assist: Medialab के रोज़मर्रा के काम के लिए TypeScript वेब हेल्पर।",
               "Bangkit Academy 2024 कैपस्टोन (मोबाइल): इंडोनेशिया के छोटे व्यवसायों के लिए आसान टैक्स।",
               "ब्राउज़र में सेंटिमेंट एनालिसिस: टेक्स्ट अंदर, मूड बाहर।"],
    "footer": "sedotan bekas — dipakai sekali, masih berguna · एक बार इस्तेमाल, अब भी काम की · अंतिम जाँच {date}, {time} WIB",
    "md_caption": "<b><i>sedotan bekas</i></b> (इंडोनेशियाई, संज्ञा): इस्तेमाल की हुई स्ट्रॉ। एक बार इस्तेमाल हुई, फिर भी काम की।",
    "md_abs_h": "> सार",
    "md_abs": ("मैं **PT Medialab Indonesia** की परीक्षण प्रयोगशाला के लिए इन-हाउस सॉफ़्टवेयर बनाता हूँ, जिसमें सबसे अहम है इसका **LIMS**\n"
               "(Next.js · Prisma · MariaDB, जिसे GitHub Actions, PM2 और Nginx के ज़रिए Ubuntu पर डिप्लॉय किया जाता है)। फिर मैं खुद उसका\n"
               "पेनटेस्ट करता हूँ, ताकि बग किसी और से पहले मुझसे टकराएँ। **Politeknik Negeri Jakarta** से इन्फ़ॉर्मेटिक्स इंजीनियरिंग में\n"
               "स्नातक और Bangkit Academy 2024 (मोबाइल डेवलपमेंट) का पूर्व छात्र।"),
    "md_samples_h": "> परीक्षण मेज़ पर नमूने",
    "alt_el": "मेरी प्रोग्रामिंग भाषाओं और टूल्स की आवर्त सारणी", "alt_ch": "पिछले 120 दिनों के दैनिक योगदान का क्रोमैटोग्राम",
}

T["es"] = {
    "native": "Español", "dir": "ltr", "dec": ",", "months": "ene feb mar abr may jun jul ago sept oct nov dic".split(),
    "date": "{d} {mon} {y}", "short": "{d} {mon}",
    "days": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    "fig": "FIG. 01 — MUESTRA {code} · RECIBIDA {date}",
    "taglines": ["construye el LIMS. luego intenta romperlo.", "Next.js · Prisma · MariaDB · Nginx · PM2",
                 "Bangkit Academy 2024 · Desarrollo móvil", "sedotan bekas: una pajita usada. todavía sorbe."],
    "labels": ["CARGO", "ORIGEN", "ENSAYO"],
    "role_v": "Ingeniero de software · PT Medialab Indonesia",
    "origin_v": "Ing. Informática · Politeknik Negeri Jakarta",
    "assay_v": "{n} contribuciones / 365 d · {r} repos públicos · desde {y}",
    "coa_sub": "Certificado de análisis — muestra: un (1) desarrollador",
    "coa": {
        "cols": ["N.º", "Parámetro", "Resultado", "Unidad", "Límite", "Método", "Obs."],
        "rows": ["Contribuciones totales", "Media diaria", "Racha actual", "Racha más larga", "Pico diario",
                 "Día más activo", "Compuesto dominante (por bytes)", "Nivel de cafeína*", "Bugs que escaparon*"],
        "u": {"contrib": "contrib.", "perday": "por día", "days": "días", "cups": "tazas/día", "release": "por versión"},
        "l_notreg": "no regulado", "m_organo": "Organoléptico", "m_pentest": "Pentest propio",
        "meta_l": ["N.º", "Fecha", "Página"], "page_v": "1 / 1",
        "info_l": ["Muestra", "Código", "Matriz", "Recibida", "Periodo", "Muestreo"],
        "matrix_v": "Código, café y plazos", "sampling_v": "Compuesta de 365 días · GitHub API",
    },
    "notes": ["* Parámetro no acreditado.", "Hasil uji hanya berlaku untuk sampel yang diuji.",
              "Los resultados solo se refieren a la muestra ensayada.",
              "LoD = límite de detección · IK = instrucción de trabajo interna",
              "Reanalizado automáticamente cada día a las 00:17 WIB por github-actions[bot]."],
    "approved": "Disahkan oleh / Aprobado por", "sig_title": "Penyelia Teknis · Supervisor técnico",
    "el_mass": "MASA = % DEL CÓDIGO (BYTES)", "el_assayed": "{n} repos analizados · sin lenguajes de marcado",
    "el_tools": "* SERI ALAT · SERIE DE HERRAMIENTAS", "last_assay": "último ensayo {date} · {time} WIB",
    "ch_sub": "actividad de commits", "ch_det": "DETECTOR: UV-GIT @ 254 NM",
    "ch_col": "columna: {user}/* · ventana: {n} d · 1 analista", "ch_x": "tiempo de retención →", "ch_y": "intensidad",
    "ch_sum": "∑ área ({n} d) = {win} · picos ≥ 20: {big} · máx. {max} @ {date}",
    "s_sample": "MUESTRA", "s_last": "ÚLTIMO MUESTREO",
    "s_desc": ["Sistema de gestión de información de laboratorio para el laboratorio de ensayos de PT Medialab Indonesia.",
               "MediaLab Assist: una herramienta web en TypeScript para el trabajo diario en Medialab.",
               "Proyecto final de Bangkit Academy 2024 (parte móvil): impuestos fáciles para las pymes de Indonesia.",
               "Análisis de sentimiento en el navegador: entra texto, sale estado de ánimo."],
    "footer": "sedotan bekas — dipakai sekali, masih berguna · usada una vez, todavía útil · último ensayo {date}, {time} WIB",
    "md_caption": "<b><i>sedotan bekas</i></b> (sust., indonesio): una pajita usada. Ya se usó una vez, pero sigue sirviendo.",
    "md_abs_h": "> resumen",
    "md_abs": ("Desarrollo el software interno del laboratorio de ensayos de **PT Medialab Indonesia**, sobre todo su **LIMS**\n"
               "(Next.js · Prisma · MariaDB, desplegado en Ubuntu con GitHub Actions, PM2 y Nginx). Después le hago pentesting yo mismo,\n"
               "para que los bugs me encuentren a mí antes que a nadie. Graduado en Ingeniería Informática por la **Politeknik Negeri Jakarta**\n"
               "y exalumno de Bangkit Academy 2024 (Desarrollo móvil)."),
    "md_samples_h": "> muestras en la mesa",
    "alt_el": "Tabla periódica de los lenguajes y herramientas que uso",
    "alt_ch": "Cromatograma de mis contribuciones diarias en los últimos 120 días",
}

T["ar"] = {
    "native": "العربية", "dir": "rtl", "dec": ".",
    "months": ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
    "date": "{d} {mon} {y}", "short": "{d} {mon}",
    "days": ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"],
    "fig": "شكل 01 — عيّنة {code} · تاريخ الاستلام {date}",
    "taglines": ["أبني نظام LIMS، ثم أحاول اختراقه.", "Next.js · Prisma · MariaDB · Nginx · PM2",
                 "Bangkit Academy 2024 · تطوير تطبيقات الجوال", "sedotan bekas: ماصّة مستعملة، وما زالت تعمل."],
    "labels": ["الوظيفة", "الدراسة", "الفحص"],
    "role_v": "مهندس برمجيات · PT Medialab Indonesia",
    "origin_v": "هندسة المعلوماتية · Politeknik Negeri Jakarta",
    "assay_v": "{n} مساهمة خلال 365 يومًا · {r} مستودعًا عامًا · منذ {y}",
    "coa_sub": "شهادة تحليل — العيّنة: مطوّر واحد (1)",
    "coa": {
        "cols": ["م", "المعيار", "النتيجة", "الوحدة", "الحد", "الطريقة", "ملاحظة"],
        "rows": ["إجمالي المساهمات", "المتوسط اليومي", "السلسلة الحالية", "أطول سلسلة", "الذروة اليومية",
                 "أكثر الأيام نشاطًا", "المركّب السائد (بالبايت)", "مستوى الكافيين*", "أخطاء أفلتت*"],
        "u": {"contrib": "مساهمة", "perday": "يوميًا", "days": "يوم", "cups": "كوب/يوم", "release": "لكل إصدار"},
        "l_notreg": "غير محدد", "m_organo": "حسّي", "m_pentest": "اختبار اختراق ذاتي",
        "meta_l": ["الرقم", "التاريخ", "الصفحة"], "page_v": "1 / 1",
        "info_l": ["اسم العيّنة", "رمز العيّنة", "المصفوفة", "الاستلام", "فترة الفحص", "أخذ العيّنات"],
        "matrix_v": "برمجة وقهوة ومواعيد تسليم", "sampling_v": "عيّنة مركّبة لـ365 يومًا · GitHub API",
    },
    "notes": ["* معيار غير معتمد.", "Hasil uji hanya berlaku untuk sampel yang diuji.",
              "تنطبق هذه النتائج على العيّنة المفحوصة فقط.", "LoD = حد الكشف · IK = تعليمات عمل داخلية",
              "يُعاد التحليل تلقائيًا كل يوم الساعة 00:17 بتوقيت WIB بواسطة github-actions[bot]."],
    "approved": "Disahkan oleh / اعتمده", "sig_title": "Penyelia Teknis · مشرف فني",
    "el_mass": "الكتلة = نسبة الشيفرة (بالبايت)", "el_assayed": "تم فحص {n} مستودعًا · باستثناء لغات الترميز",
    "el_tools": "* SERI ALAT · سلسلة الأدوات", "last_assay": "آخر فحص {date} · {time} WIB",
    "ch_sub": "نشاط الإيداعات", "ch_det": "الكاشف: UV-GIT @ 254 NM",
    "ch_col": "العمود: {user}/* · النافذة: {n} يومًا · محلل واحد", "ch_x": "زمن الاحتجاز", "ch_y": "الشدة",
    "ch_sum": "∑ المساحة ({n} يومًا) = {win} · القمم ≥ 20: {big} · الأقصى {max} @ {date}",
    "s_sample": "عيّنة", "s_last": "آخر أخذ عيّنة",
    "s_desc": ["نظام إدارة معلومات المختبر (LIMS) لمختبر الفحص في PT Medialab Indonesia.",
               "MediaLab Assist: أداة ويب بلغة TypeScript للعمل اليومي في Medialab.",
               "مشروع تخرّج Bangkit Academy 2024 (الجوال): ضرائب سهلة للمشاريع الصغيرة في إندونيسيا.",
               "تحليل المشاعر في المتصفح: يدخل النص، ويخرج المزاج."],
    "footer": "sedotan bekas — dipakai sekali, masih berguna · استُعملت مرة، وما زالت مفيدة · آخر فحص {date}، {time} WIB",
    "md_caption": "<b><i>sedotan bekas</i></b> (اسم، بالإندونيسية): ماصّة مستعملة. استُعملت مرة، وما زالت مفيدة.",
    "md_abs_h": "> ملخّص",
    "md_abs": ("أطوّر البرمجيات الداخلية لمختبر الفحص في **PT Medialab Indonesia**، وأبرزها نظام **LIMS** الخاص به\n"
               "(Next.js · Prisma · MariaDB، ويُنشر على Ubuntu عبر GitHub Actions وPM2 وNginx). ثم أُجري عليه اختبار الاختراق بنفسي،\n"
               "لكي تصطدم الأخطاء بي قبل أن تصل إلى أي شخص آخر. خرّيج هندسة المعلوماتية من **Politeknik Negeri Jakarta**،\n"
               "ومن خرّيجي Bangkit Academy 2024 (تطوير تطبيقات الجوال)."),
    "md_samples_h": "> عيّنات على طاولة الفحص",
    "alt_el": "جدول دوري للغات البرمجة والأدوات التي أستخدمها", "alt_ch": "كروماتوغرام مساهماتي اليومية خلال آخر 120 يومًا",
}

T["fr"] = {
    "native": "Français", "dir": "ltr", "dec": ",",
    "months": "janv. févr. mars avr. mai juin juil. août sept. oct. nov. déc.".split(),
    "date": "{d} {mon} {y}", "short": "{d} {mon}",
    "days": ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
    "fig": "FIG. 01 — ÉCHANTILLON {code} · REÇU LE {date}",
    "taglines": ["construit le LIMS. puis tente de le casser.", "Next.js · Prisma · MariaDB · Nginx · PM2",
                 "Bangkit Academy 2024 · Développement mobile", "sedotan bekas : une paille usagée. elle aspire encore."],
    "labels": ["POSTE", "FORMATION", "ESSAI"],
    "role_v": "Ingénieur logiciel · PT Medialab Indonesia",
    "origin_v": "Génie informatique · Politeknik Negeri Jakarta",
    "assay_v": "{n} contributions / 365 j · {r} dépôts publics · depuis {y}",
    "coa_sub": "Certificat d’analyse — échantillon : un (1) développeur",
    "coa": {
        "cols": ["N°", "Paramètre", "Résultat", "Unité", "Limite", "Méthode", "Rem."],
        "rows": ["Contributions totales", "Moyenne journalière", "Série en cours", "Plus longue série", "Pic journalier",
                 "Jour le plus actif", "Composé dominant (en octets)", "Taux de caféine*", "Bugs échappés*"],
        "u": {"contrib": "contrib.", "perday": "par jour", "days": "jours", "cups": "tasses/jour", "release": "par version"},
        "l_notreg": "non réglementé", "m_organo": "Organoleptique", "m_pentest": "Pentest maison",
        "meta_l": ["N°", "Date", "Page"], "page_v": "1 / 1",
        "info_l": ["Échantillon", "Code", "Matrice", "Reçu le", "Période", "Prélèvement"],
        "matrix_v": "Code, café et deadlines", "sampling_v": "Composite sur 365 jours · GitHub API",
    },
    "notes": ["* Paramètre non accrédité.", "Hasil uji hanya berlaku untuk sampel yang diuji.",
              "Ces résultats ne concernent que l’échantillon testé.",
              "LoD = limite de détection · IK = instruction de travail interne",
              "Réanalysé automatiquement chaque jour à 00:17 WIB par github-actions[bot]."],
    "approved": "Disahkan oleh / Approuvé par", "sig_title": "Penyelia Teknis · Superviseur technique",
    "el_mass": "MASSE = % DU CODE (OCTETS)", "el_assayed": "{n} dépôts analysés · balisage exclu",
    "el_tools": "* SERI ALAT · SÉRIE OUTILS", "last_assay": "dernier essai {date} · {time} WIB",
    "ch_sub": "activité des commits", "ch_det": "DÉTECTEUR : UV-GIT @ 254 NM",
    "ch_col": "colonne : {user}/* · fenêtre : {n} j · 1 analyste", "ch_x": "temps de rétention →", "ch_y": "intensité",
    "ch_sum": "∑ aire ({n} j) = {win} · pics ≥ 20 : {big} · max {max} @ {date}",
    "s_sample": "ÉCHANTILLON", "s_last": "DERNIER PRÉLÈVEMENT",
    "s_desc": ["Système de gestion de l’information de laboratoire pour le labo d’essais de PT Medialab Indonesia.",
               "MediaLab Assist : un outil web en TypeScript pour le travail quotidien chez Medialab.",
               "Projet final Bangkit Academy 2024 (volet mobile) : l’impôt facile pour les PME indonésiennes.",
               "Analyse de sentiment dans le navigateur : du texte en entrée, une humeur en sortie."],
    "footer": "sedotan bekas — dipakai sekali, masih berguna · utilisée une fois, toujours utile · dernier essai {date}, {time} WIB",
    "md_caption": "<b><i>sedotan bekas</i></b> (n., indonésien) : une paille usagée. Déjà servie une fois, toujours utile.",
    "md_abs_h": "> résumé",
    "md_abs": ("Je développe les logiciels internes du laboratoire d’essais de **PT Medialab Indonesia**, à commencer par son **LIMS**\n"
               "(Next.js · Prisma · MariaDB, déployé sur Ubuntu avec GitHub Actions, PM2 et Nginx). Ensuite, je le pentest moi-même,\n"
               "pour que les bugs tombent sur moi avant de tomber sur quelqu’un d’autre. Diplômé en génie informatique de la\n"
               "**Politeknik Negeri Jakarta** et ancien de Bangkit Academy 2024 (Développement mobile)."),
    "md_samples_h": "> échantillons sur la paillasse",
    "alt_el": "Tableau périodique des langages et outils que j’utilise",
    "alt_ch": "Chromatogramme de mes contributions quotidiennes sur les 120 derniers jours",
}

T["bn"] = {
    "native": "বাংলা", "dir": "ltr", "dec": ".",
    "months": ["জানু", "ফেব", "মার্চ", "এপ্রি", "মে", "জুন", "জুল", "আগ", "সেপ", "অক্টো", "নভে", "ডিসে"],
    "date": "{d} {mon} {y}", "short": "{d} {mon}",
    "days": ["সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার", "শনিবার", "রবিবার"],
    "fig": "চিত্র 01 — নমুনা {code} · প্রাপ্তি {date}",
    "taglines": ["LIMS বানাই, তারপর সেটা ভাঙার চেষ্টা করি।", "Next.js · Prisma · MariaDB · Nginx · PM2",
                 "Bangkit Academy 2024 · মোবাইল ডেভেলপমেন্ট", "sedotan bekas: ব্যবহার করা স্ট্র, এখনও কাজের।"],
    "labels": ["পদ", "শিক্ষা", "পরীক্ষা"],
    "role_v": "সফটওয়্যার ইঞ্জিনিয়ার · PT Medialab Indonesia",
    "origin_v": "ইনফরমেটিক্স ইঞ্জিনিয়ারিং · Politeknik Negeri Jakarta",
    "assay_v": "365 দিনে {n}টি অবদান · {r}টি পাবলিক রিপো · {y} থেকে",
    "coa_sub": "বিশ্লেষণ সনদ — নমুনা: একজন (1) ডেভেলপার",
    "coa": {
        "cols": ["নং", "প্যারামিটার", "ফলাফল", "একক", "সীমা", "পদ্ধতি", "মন্তব্য"],
        "rows": ["মোট অবদান", "দৈনিক গড়", "চলতি স্ট্রিক", "দীর্ঘতম স্ট্রিক", "দৈনিক সর্বোচ্চ", "সবচেয়ে ব্যস্ত বার",
                 "প্রধান যৌগ (বাইট অনুযায়ী)", "ক্যাফেইনের মাত্রা*", "ফসকে যাওয়া বাগ*"],
        "u": {"contrib": "অবদান", "perday": "প্রতিদিন", "days": "দিন", "cups": "কাপ/দিন", "release": "প্রতি রিলিজ"},
        "l_notreg": "নিয়ন্ত্রিত নয়", "m_organo": "অর্গানোলেপটিক", "m_pentest": "নিজস্ব পেনটেস্ট",
        "meta_l": ["নং", "তারিখ", "পৃষ্ঠা"], "page_v": "1 / 1",
        "info_l": ["নমুনার নাম", "নমুনা কোড", "ম্যাট্রিক্স", "প্রাপ্তি", "পরীক্ষার সময়কাল", "নমুনা সংগ্রহ"],
        "matrix_v": "কোড, কফি আর ডেডলাইন", "sampling_v": "365 দিনের মিশ্র নমুনা · GitHub API",
    },
    "notes": ["* এই প্যারামিটার স্বীকৃত নয়।", "Hasil uji hanya berlaku untuk sampel yang diuji.",
              "এই ফলাফল শুধু পরীক্ষিত নমুনার ক্ষেত্রে প্রযোজ্য।", "LoD = শনাক্তকরণ সীমা · IK = অভ্যন্তরীণ কাজের নির্দেশিকা",
              "github-actions[bot] প্রতিদিন 00:17 WIB-এ নিজে থেকে আবার বিশ্লেষণ করে।"],
    "approved": "Disahkan oleh / অনুমোদনকারী", "sig_title": "Penyelia Teknis · কারিগরি তত্ত্বাবধায়ক",
    "el_mass": "ভর = কোডের % (বাইট)", "el_assayed": "{n}টি রিপো পরীক্ষিত · মার্কআপ বাদ",
    "el_tools": "* SERI ALAT · টুল সিরিজ", "last_assay": "শেষ পরীক্ষা {date} · {time} WIB",
    "ch_sub": "কমিট কার্যকলাপ", "ch_det": "ডিটেক্টর: UV-GIT @ 254 NM",
    "ch_col": "কলাম: {user}/* · সময়সীমা: {n} দিন · 1 জন বিশ্লেষক", "ch_x": "রিটেনশন টাইম →", "ch_y": "তীব্রতা",
    "ch_sum": "∑ ক্ষেত্রফল ({n} দিন) = {win} · ≥ 20 শিখর: {big} · সর্বোচ্চ {max} @ {date}",
    "s_sample": "নমুনা", "s_last": "শেষ নমুনা",
    "s_desc": ["PT Medialab Indonesia-র পরীক্ষাগারের জন্য ল্যাবরেটরি ইনফরমেশন ম্যানেজমেন্ট সিস্টেম।",
               "MediaLab Assist: Medialab-এর প্রতিদিনের কাজের জন্য TypeScript ওয়েব সহকারী।",
               "Bangkit Academy 2024 ক্যাপস্টোন (মোবাইল): ইন্দোনেশিয়ার ছোট ব্যবসার জন্য সহজ কর।",
               "ব্রাউজারে সেন্টিমেন্ট অ্যানালাইসিস: লেখা ঢোকে, মেজাজ বের হয়।"],
    "footer": "sedotan bekas — dipakai sekali, masih berguna · একবার ব্যবহৃত, এখনও কাজের · শেষ পরীক্ষা {date}, {time} WIB",
    "md_caption": "<b><i>sedotan bekas</i></b> (বিশেষ্য, ইন্দোনেশীয়): ব্যবহার করা স্ট্র। একবার ব্যবহার হয়েছে, তবু এখনও কাজের।",
    "md_abs_h": "> সারাংশ",
    "md_abs": ("আমি **PT Medialab Indonesia**-র পরীক্ষাগারের জন্য ইন-হাউস সফটওয়্যার তৈরি করি, যার মধ্যে সবচেয়ে গুরুত্বপূর্ণ হলো এর **LIMS**\n"
               "(Next.js · Prisma · MariaDB, GitHub Actions, PM2 ও Nginx দিয়ে Ubuntu-তে ডিপ্লয় করা)। তারপর আমি নিজেই সেটার পেনটেস্ট করি,\n"
               "যাতে বাগগুলো অন্য কারও আগে আমার সামনে পড়ে। **Politeknik Negeri Jakarta** থেকে ইনফরমেটিক্স ইঞ্জিনিয়ারিংয়ে স্নাতক\n"
               "এবং Bangkit Academy 2024 (মোবাইল ডেভেলপমেন্ট)-এর প্রাক্তন শিক্ষার্থী।"),
    "md_samples_h": "> পরীক্ষার টেবিলে নমুনা",
    "alt_el": "আমার প্রোগ্রামিং ভাষা ও টুলের পর্যায় সারণি", "alt_ch": "গত 120 দিনের দৈনিক অবদানের ক্রোমাটোগ্রাম",
}

T["pt"] = {
    "native": "Português", "dir": "ltr", "dec": ",", "months": "jan fev mar abr mai jun jul ago set out nov dez".split(),
    "date": "{d} {mon} {y}", "short": "{d} {mon}",
    "days": ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"],
    "fig": "FIG. 01 — AMOSTRA {code} · RECEBIDA EM {date}",
    "taglines": ["constrói o LIMS. depois tenta quebrá-lo.", "Next.js · Prisma · MariaDB · Nginx · PM2",
                 "Bangkit Academy 2024 · Desenvolvimento mobile", "sedotan bekas: um canudo usado. ainda dá pra sugar."],
    "labels": ["CARGO", "FORMAÇÃO", "ENSAIO"],
    "role_v": "Engenheiro de software · PT Medialab Indonesia",
    "origin_v": "Eng. Informática · Politeknik Negeri Jakarta",
    "assay_v": "{n} contribuições / 365 d · {r} repos públicos · desde {y}",
    "coa_sub": "Certificado de análise — amostra: um (1) desenvolvedor",
    "coa": {
        "cols": ["Nº", "Parâmetro", "Resultado", "Unidade", "Limite", "Método", "Obs."],
        "rows": ["Contribuições totais", "Média diária", "Sequência atual", "Maior sequência", "Pico diário",
                 "Dia mais ativo", "Composto dominante (por bytes)", "Nível de cafeína*", "Bugs que escaparam*"],
        "u": {"contrib": "contrib.", "perday": "por dia", "days": "dias", "cups": "xícaras/dia", "release": "por versão"},
        "l_notreg": "não regulado", "m_organo": "Organoléptico", "m_pentest": "Pentest próprio",
        "meta_l": ["Nº", "Data", "Página"], "page_v": "1 / 1",
        "info_l": ["Amostra", "Código", "Matriz", "Recebida em", "Período", "Amostragem"],
        "matrix_v": "Código, café e prazos", "sampling_v": "Composta de 365 dias · GitHub API",
    },
    "notes": ["* Parâmetro não acreditado.", "Hasil uji hanya berlaku untuk sampel yang diuji.",
              "Os resultados referem-se apenas à amostra ensaiada.",
              "LoD = limite de detecção · IK = instrução de trabalho interna",
              "Reanalisado automaticamente todo dia às 00:17 WIB pelo github-actions[bot]."],
    "approved": "Disahkan oleh / Aprovado por", "sig_title": "Penyelia Teknis · Supervisor técnico",
    "el_mass": "MASSA = % DO CÓDIGO (BYTES)", "el_assayed": "{n} repos analisados · sem linguagens de marcação",
    "el_tools": "* SERI ALAT · SÉRIE DE FERRAMENTAS", "last_assay": "último ensaio {date} · {time} WIB",
    "ch_sub": "atividade de commits", "ch_det": "DETECTOR: UV-GIT @ 254 NM",
    "ch_col": "coluna: {user}/* · janela: {n} d · 1 analista", "ch_x": "tempo de retenção →", "ch_y": "intensidade",
    "ch_sum": "∑ área ({n} d) = {win} · picos ≥ 20: {big} · máx. {max} @ {date}",
    "s_sample": "AMOSTRA", "s_last": "ÚLTIMA AMOSTRAGEM",
    "s_desc": ["Sistema de gestão de informações laboratoriais para o laboratório de ensaios da PT Medialab Indonesia.",
               "MediaLab Assist: uma ferramenta web em TypeScript para o dia a dia na Medialab.",
               "Projeto final da Bangkit Academy 2024 (parte mobile): imposto fácil para pequenas empresas da Indonésia.",
               "Análise de sentimento no navegador: entra texto, sai o humor."],
    "footer": "sedotan bekas — dipakai sekali, masih berguna · usado uma vez, ainda útil · último ensaio {date}, {time} WIB",
    "md_caption": "<b><i>sedotan bekas</i></b> (subst., indonésio): um canudo usado. Já foi usado uma vez, mas ainda serve.",
    "md_abs_h": "> resumo",
    "md_abs": ("Desenvolvo os sistemas internos do laboratório de ensaios da **PT Medialab Indonesia**, principalmente o **LIMS**\n"
               "(Next.js · Prisma · MariaDB, publicado no Ubuntu com GitHub Actions, PM2 e Nginx). Depois eu mesmo faço o pentest,\n"
               "para que os bugs me encontrem antes de encontrar qualquer outra pessoa. Formado em Engenharia Informática pela\n"
               "**Politeknik Negeri Jakarta** e ex-aluno da Bangkit Academy 2024 (Desenvolvimento mobile)."),
    "md_samples_h": "> amostras na bancada",
    "alt_el": "Tabela periódica das linguagens e ferramentas que uso",
    "alt_ch": "Cromatograma das minhas contribuições diárias nos últimos 120 dias",
}

T["ru"] = {
    "native": "Русский", "dir": "ltr", "dec": ",",
    "months": "янв. февр. мар. апр. мая июн. июл. авг. сент. окт. нояб. дек.".split(),
    "date": "{d} {mon} {y}", "short": "{d} {mon}",
    "days": ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"],
    "fig": "РИС. 01 — ОБРАЗЕЦ {code} · ПОЛУЧЕН {date}",
    "taglines": ["пишет LIMS. потом пытается её взломать.", "Next.js · Prisma · MariaDB · Nginx · PM2",
                 "Bangkit Academy 2024 · мобильная разработка", "sedotan bekas: использованная трубочка. ещё тянет."],
    "labels": ["РОЛЬ", "УЧЁБА", "АНАЛИЗ"],
    "role_v": "Инженер-программист · PT Medialab Indonesia",
    "origin_v": "Информатика · Politeknik Negeri Jakarta",
    "assay_v": "вкладов за 365 дн.: {n} · публичных репо: {r} · с {y} г.",
    "coa_sub": "Сертификат анализа — образец: один (1) разработчик",
    "coa": {
        "cols": ["№", "Показатель", "Результат", "Ед. изм.", "Норматив", "Метод", "Прим."],
        "rows": ["Всего вкладов", "Среднее в день", "Текущая серия", "Самая длинная серия", "Дневной пик",
                 "Самый активный день", "Основное вещество (по байтам)", "Содержание кофеина*", "Пропущенные баги*"],
        "u": {"contrib": "шт.", "perday": "в день", "days": "дн.", "cups": "чашек/день", "release": "на релиз"},
        "l_notreg": "не нормируется", "m_organo": "Органолептика", "m_pentest": "Свой пентест",
        "meta_l": ["№", "Дата", "Стр."], "page_v": "1 / 1",
        "info_l": ["Образец", "Код образца", "Матрица", "Получен", "Период", "Отбор проб"],
        "matrix_v": "Код, кофе и дедлайны", "sampling_v": "Сборная проба за 365 дней · GitHub API",
    },
    "notes": ["* Показатель не аккредитован.", "Hasil uji hanya berlaku untuk sampel yang diuji.",
              "Результаты относятся только к испытанному образцу.",
              "LoD = предел обнаружения · IK = внутренняя рабочая инструкция",
              "Повторный анализ каждый день в 00:17 WIB выполняет github-actions[bot]."],
    "approved": "Disahkan oleh / Утвердил", "sig_title": "Penyelia Teknis · Технический руководитель",
    "el_mass": "МАССА = % КОДА (БАЙТЫ)", "el_assayed": "проверено репо: {n} · без языков разметки",
    "el_tools": "* SERI ALAT · СЕРИЯ ИНСТРУМЕНТОВ", "last_assay": "последний анализ {date} · {time} WIB",
    "ch_sub": "активность коммитов", "ch_det": "ДЕТЕКТОР: UV-GIT @ 254 НМ",
    "ch_col": "колонка: {user}/* · окно: {n} дн. · 1 аналитик", "ch_x": "время удерживания →", "ch_y": "интенсивность",
    "ch_sum": "∑ площадь ({n} дн.) = {win} · пики ≥ 20: {big} · макс. {max} @ {date}",
    "s_sample": "ОБРАЗЕЦ", "s_last": "ПОСЛЕДНИЙ ОТБОР",
    "s_desc": ["Лабораторная информационная система (LIMS) для испытательной лаборатории PT Medialab Indonesia.",
               "MediaLab Assist: веб-помощник на TypeScript для повседневной работы в Medialab.",
               "Выпускной проект Bangkit Academy 2024 (мобильная часть): простые налоги для малого бизнеса Индонезии.",
               "Анализ тональности в браузере: на входе текст, на выходе настроение."],
    "footer": "sedotan bekas — dipakai sekali, masih berguna · использована раз, всё ещё полезна · последний анализ {date}, {time} WIB",
    "md_caption": "<b><i>sedotan bekas</i></b> (сущ., индонезийский): использованная трубочка. Уже послужила, но ещё пригодится.",
    "md_abs_h": "> аннотация",
    "md_abs": ("Я разрабатываю внутренние системы для испытательной лаборатории **PT Medialab Indonesia**, прежде всего её **LIMS**\n"
               "(Next.js · Prisma · MariaDB, развёртывание на Ubuntu через GitHub Actions, PM2 и Nginx). Потом сам провожу её пентест,\n"
               "чтобы баги встретились со мной раньше, чем с кем-то ещё. Окончил **Politeknik Negeri Jakarta** по специальности\n"
               "«Информатика», выпускник Bangkit Academy 2024 (мобильная разработка)."),
    "md_samples_h": "> образцы на лабораторном столе",
    "alt_el": "Периодическая таблица языков и инструментов, с которыми я работаю",
    "alt_ch": "Хроматограмма моих ежедневных вкладов за последние 120 дней",
}


def coa_strings(lang):
    """(primary, secondary) dicts for the lab report table."""
    if lang in ("en", "id"):
        return COA_ID, COA_EN
    return T[lang]["coa"], COA_ID


def all_text(lang):
    """Every string a language can render — used to build its font subset."""
    out = []

    def walk(v):
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                walk(x)
    walk(T[lang])
    walk(coa_strings(lang))
    return "".join(out)


# ── Attachment card: the portfolio website ("Lampiran A") ─────────────────
# att_stats are the labels under the numbers in build.py's PORTFOLIO_STATS (same order).
ATT = {
    "en": {"att_tag": "LAMPIRAN A · ATTACHMENT A", "att_title": "The full case file", "att_sub": "portfolio",
           "att_note": "LIMS case study · numbers · experience · credentials", "att_cta": "OPEN PORTFOLIO ↗",
           "att_stats": ["unit tests gate every release", "screens, grown from 18", "unwritten lab rules turned into logic",
                         "days from feedback to release"]},
    "id": {"att_tag": "LAMPIRAN A", "att_title": "Berkas kasus lengkap", "att_sub": "portofolio",
           "att_note": "studi kasus LIMS · angka · pengalaman · kredensial", "att_cta": "BUKA PORTOFOLIO ↗",
           "att_stats": ["unit test menjaga tiap rilis", "layar, tumbuh dari 18", "aturan lab tak tertulis jadi logika",
                         "hari dari masukan sampai rilis"]},
    "zh": {"att_tag": "LAMPIRAN A · 附件 A", "att_title": "完整案例档案", "att_sub": "作品集",
           "att_note": "LIMS 案例 · 数据 · 经历 · 资历", "att_cta": "打开作品集 ↗",
           "att_stats": ["个单元测试为每次发布把关", "个页面，由 18 个扩展而来", "条不成文的实验室规则写进系统", "天：从反馈到上线"]},
    "hi": {"att_tag": "LAMPIRAN A · संलग्नक A", "att_title": "पूरी केस फ़ाइल", "att_sub": "पोर्टफ़ोलियो",
           "att_note": "LIMS केस स्टडी · आँकड़े · अनुभव · प्रमाणपत्र", "att_cta": "पोर्टफ़ोलियो खोलें ↗",
           "att_stats": ["यूनिट टेस्ट हर रिलीज़ की जाँच करते हैं", "स्क्रीन, 18 से बढ़कर", "अलिखित लैब नियम सिस्टम लॉजिक बने",
                         "दिन: फ़ीडबैक से रिलीज़ तक"]},
    "es": {"att_tag": "LAMPIRAN A · ANEXO A", "att_title": "El expediente completo", "att_sub": "portafolio",
           "att_note": "caso LIMS · cifras · experiencia · credenciales", "att_cta": "VER PORTAFOLIO ↗",
           "att_stats": ["tests unitarios protegen cada versión", "pantallas, desde 18", "reglas no escritas del laboratorio, ahora lógica",
                         "días de la retroalimentación al despliegue"]},
    "ar": {"att_tag": "LAMPIRAN A · المرفق A", "att_title": "الملف الكامل", "att_sub": "معرض الأعمال",
           "att_note": "دراسة حالة LIMS · أرقام · خبرة · مؤهلات", "att_cta": "افتح معرض الأعمال ↗",
           "att_stats": ["اختبار وحدة يحرس كل إصدار", "شاشة، بعد أن كانت 18", "قاعدة مخبرية غير مكتوبة صارت منطقًا",
                         "أيام من الملاحظات إلى الإصدار"]},
    "fr": {"att_tag": "LAMPIRAN A · ANNEXE A", "att_title": "Le dossier complet", "att_sub": "portfolio",
           "att_note": "étude de cas LIMS · chiffres · parcours · diplômes", "att_cta": "OUVRIR LE PORTFOLIO ↗",
           "att_stats": ["tests unitaires avant chaque mise en prod", "écrans, partis de 18", "règles non écrites du labo devenues logique",
                         "jours entre retour et mise en prod"]},
    "bn": {"att_tag": "LAMPIRAN A · সংযুক্তি A", "att_title": "পূর্ণ কেস ফাইল", "att_sub": "পোর্টফোলিও",
           "att_note": "LIMS কেস স্টাডি · সংখ্যা · অভিজ্ঞতা · সনদ", "att_cta": "পোর্টফোলিও খুলুন ↗",
           "att_stats": ["ইউনিট টেস্ট প্রতিটি রিলিজ পাহারা দেয়", "স্ক্রিন, 18 থেকে বেড়ে", "অলিখিত ল্যাব নিয়ম এখন সিস্টেম লজিক",
                         "দিন: ফিডব্যাক থেকে রিলিজ"]},
    "pt": {"att_tag": "LAMPIRAN A · ANEXO A", "att_title": "O dossiê completo", "att_sub": "portfólio",
           "att_note": "estudo de caso LIMS · números · experiência · credenciais", "att_cta": "ABRIR PORTFÓLIO ↗",
           "att_stats": ["testes unitários protegem cada versão", "telas, a partir de 18", "regras não escritas do laboratório viraram lógica",
                         "dias do feedback ao deploy"]},
    "ru": {"att_tag": "LAMPIRAN A · ПРИЛОЖЕНИЕ A", "att_title": "Полное досье", "att_sub": "портфолио",
           "att_note": "кейс LIMS · цифры · опыт · квалификация", "att_cta": "ОТКРЫТЬ ПОРТФОЛИО ↗",
           "att_stats": ["юнит-тестов перед каждым релизом", "экранов, начинали с 18", "неписаных правил лаборатории стали логикой",
                         "дня от отзыва до релиза"]},
}
for _L, _v in ATT.items():
    T[_L].update(_v)
