---
title: X Video Scripts — Urban sprawl, Deforestation, "Indraja < 2 menit"
type: note
date: 2026-06-27
ai-first: true
tags: [social-media, x-twitter, video, scripts, remote-sensing, jalmiburung]
account: "@jalmiburung"
stack: Remotion + Claude + ElevenLabs (Indonesian voice)
---
# X Video Scripts — @jalmiburung

## For future Claude

Three production-ready video scripts for @jalmiburung, built on his proven formula (video + stakes-first hook + ngedumel voice) from [[X-insights]]. Each has word-for-word Indonesian narration (voice: "Anda", punchy, a little ngedumel, occasional 😀), a shot list, on-screen text, real data sources, and the reply copy (links go in the FIRST REPLY, never the tweet body). Stack: Remotion (compositing) + ElevenLabs (ID narration) + Claude. Any statistic marked [VERIFY] must be pulled live before posting — do not fabricate numbers.

---

## VIDEO 1 — Urban sprawl: "Dulu ini sawah"
**Length:** ~40s · **Goal:** explode (reach) · **Best time:** 20:00 WIB

### Data / how to build
- Time-lapse: **Landsat (1985–present), Google Earth Engine** — `LANDSAT/LT05` + `LANDSAT/LC08` annual true-color or NDVI composites. Or **Google Earth Timelapse** for a quick grab.
- **Place that people recognize** (pick one): Bandung Selatan (Bojongsoang/Baleendah), Bekasi–Karawang sawah→industri, or Jatinangor. Recognizable place = shares.
- Export annual frames → assemble in Remotion at ~2 frames/sec.

### Narration (ElevenLabs, ID)
- **(0–4s)** "Dua puluh tahun lalu, ini sawah."
- **(4–9s)** "Sekarang? Lihat sendiri."  *(time-lapse starts running)*
- **(9–18s)** "Setiap petak hijau yang berubah jadi abu-abu — itu lumbung pangan yang berganti jadi perumahan."
- **(18–27s)** "Kita bicara swasembada beras, sambil mengubur sawah di bawah aspal. 😀"
- **(27–36s)** "Ini bukan tuduhan. Ini rekaman. Citra Landsat, gratis, sejak 1985. Satelit tak bisa dibohongi."
- **(36–40s)** "Mau lihat kota Anda sendiri? Caranya saya tulis di bawah."

### On-screen text (burn-in)
- 0s: "1985" → year counter ticking up with the time-lapse → "2025"
- 18s: lower-third: "sawah → perumahan"
- 36s: end card: "Landsat · gratis · @jalmiburung"

### First reply (the how-to + link)
> Ini citra Landsat (gratis, 1985–sekarang) saya rakit di Google Earth Engine. Begini cara membuat time-lapse kota Anda sendiri — skrip + langkahnya: [LINK di reply]

---

## VIDEO 2 — Deforestation: "Menunggu peta dari negara lain"
**Length:** ~38s · **Goal:** explode (reach) · **Best time:** 12:00 or 20:00 WIB

### Data / how to build
- Forest loss: **Hansen Global Forest Change (UMD/Google)** on GEE — `UMD/hansen/global_forest_change_*`; animate `lossyear` over Kalimantan/Sumatra. Or annual Landsat composites for true-color time-lapse.
- **Stat [VERIFY before posting]:** annual primary-forest loss for Indonesia — pull the latest figure from **Global Forest Watch (globalforestwatch.org)**. Convert ha → "lapangan bola" (1 ha ≈ 1.4 lapangan). Do NOT post a number you haven't verified.

### Narration (ElevenLabs, ID)
- **(0–5s)** "Katanya kita mau jadi negara maju."
- **(5–11s)** "Tapi untuk tahu di mana hutan kita hilang, kita masih menunggu peta dari negara lain."
- **(11–21s)** "Padahal jawabannya ada di langit. Tiap tahun, hutan seluas [VERIFY: X] lapangan bola lenyap di Kalimantan."  *(time-lapse + hectares counter)*
- **(21–30s)** "Tertangkap satelit. Setiap tahun. Gratis."
- **(30–38s)** "Bukan citra rahasia, bukan alat mahal. Yang belum kita punya cuma kemauan untuk membacanya."

### On-screen text
- counter: hectares lost ticking up, red
- 30s end card: "Hansen/UMD · open data · @jalmiburung"

### First reply
> Datanya terbuka: Hansen Global Forest Change, bisa diakses gratis di Google Earth Engine. Begini cara memetakan kehilangan hutan di wilayah Anda 👇 [LINK]

---

## SERIES — "Indraja < 2 menit"
**Length:** 60–90s each · **Goal:** bookmarks + authority (the funnel) · **Cadence:** weekly
A recurring how-to series. Rules: hook-first (never "step 1: install…"), ONE concept per episode, each standalone, fixed end card "Indraja < 2 menit · @jalmiburung", link to learning material in first reply.

### Episode format
1. **(0–6s) Hook** — a question or stakes line.
2. **(6–50s) One idea** — animation + narration.
3. **(50–70s) Payoff** — "begini cara melakukannya" (1–2 concrete steps).
4. **(end) Card** — series logo + "Materi lengkap di bawah 👇".

### Ep 1 — "Citra satelit itu angka, bukan foto"
- **(0–6s)** "Anda kira citra satelit itu foto, seperti jepretan ponsel? Bukan."
- **(6–20s)** "Ia tumpukan angka. Setiap piksel = deretan angka pantulan cahaya."  *(zoom into pixels → reveal DN numbers)*
- **(20–40s)** "Daun sehat rakus memantulkan inframerah. Air menelannya. Beton terang di mana-mana."  *(spectral curves animate)*
- **(40–60s)** "Warna di layar cuma terjemahan dari angka. Tukar band inframerah ke kanal merah — vegetasi menyala merah. Anda yang pilih."
- **(60–70s)** "Itu sebabnya penginderaan jauh, ujung-ujungnya, aritmetika. 😀"
- **Reply:** "Mau coba sendiri? Materi interaktif (gratis): [LINK]"

### Ep 2 — "Kenapa peta tutupan lahan sering salah"
- **(0–6s)** "Kenapa peta tutupan lahan sering keliru? Sawah ketuker kebun teh."
- **(6–40s)** "Karena kebanyakan peta cuma pakai citra SATU tanggal. Padahal tanaman berubah tiap musim."  *(single-date confusion vs NDVI time-series: sawah naik-turun, hutan stabil)*
- **(40–60s)** "Solusinya: lihat polanya sepanjang tahun, bukan satu potret. Sidik jari NDVI tiap kelas beda."
- **(60–70s)** "Open data + time-series = peta yang jujur."
- **Reply:** "Caranya pakai R `sits` + Sentinel-2 (gratis): [LINK]. Paper: DOI 10.1088/1755-1315/1276/1/012035"

### Ep 3 — "Kelihatan hutan, padahal bukan"
- **(0–6s)** "Dari atas, ini terlihat seperti hutan. Bukan."
- **(6–40s)** "Ini agroforest — kopi bercampur karet bercampur pohon buah. Bahkan model klasifikasi pun tertipu."  *(zoom into Cisokan mosaic)*
- **(40–65s)** "Bedanya ketahuan dari pola musiman dan tekstur, bukan dari warna sesaat. Itu kelas paling keras kepala yang pernah saya petakan."
- **Reply:** "Studi kasus DAS Cisokan: [LINK]"

---

## Production checklist (every video)
- [ ] Vertical or square (mobile-first), captions burned in (most watch muted)
- [ ] Hook visible in first 2 seconds
- [ ] ≤ 60–90s
- [ ] Link in FIRST REPLY, not tweet body
- [ ] Post at 12:00 or 20:00 WIB, engage for 20 min after
- [ ] [VERIFY] any statistic against the live source before posting
