---
title: X Video Storyline v2 — Sawah, Method & Food Security
type: note
date: 2026-06-27
ai-first: true
tags: [social-media, x-twitter, video, storyline, sawah, food-security, jalmiburung]
account: "@jalmiburung"
length: "~85s, 3 acts + provocation"
---
# X Video Storyline v2 — "Dari sawah ke pertanyaan"

## For future Claude

The longer, research-bridge version of the sawah video for @jalmiburung. Arc: (1) the change — sawah→city time-lapse; (2) HOW to analyze it — satellite/SAR phenology method; (3) current state — his S1 paddy map of Java (~2.8M ha, [[PUPR]]); (4) provocation — shrinking sawah vs 2045 food security, asked TO the audience to drive replies. Supersedes the 42s v1 ([[X-sawah-video-production]]). Needs a new asset: a Java paddy-map image. Narration in his voice (ID, "Anda", ngedumel→provocation).

## Act structure
- **ACT 1 — The change (0–17s):** time-lapse, sawah → rumah & pabrik. Hook.
- **ACT 2 — How to analyze (17–52s):** satellite = angka, not photo; each cover has a spectral signature; sawah's unique flood→grow→harvest cycle; SAR sees through cloud; train a model, map all Java.
- **ACT 3 — Current state (52–68s):** his S1 result — Java paddy ≈ 2.8M ha, but declining.
- **ACT 4 — Provocation (68–88s):** if sawah keeps shrinking, what do we eat in 2045? Population up, land down. Asked to the viewer.

## Narration (≈85s, ID — paste into make_narration.py)
> Dua puluh tahun lalu, ini sawah.
> Sekarang? Lihat sendiri.
> Hijau berubah jadi abu-abu — sawah berganti rumah dan pabrik.
> Bagaimana saya tahu? Bukan dari katanya. Dari satelit.
> Tiap tahun satelit memotret Bumi. Citranya bukan foto biasa — ia tumpukan angka. Tiap objek punya pantulan khas.
> Sawah paling khas: tergenang saat tanam, menghijau saat tumbuh, lalu dipanen. Pola itu ditangkap radar, menembus awan.
> Saya susun ribuan citra, latih model, lalu petakan seluruh Jawa: mana yang masih sawah, mana yang sudah hilang.
> Hasilnya, sawah Jawa kini sekitar dua koma tiga juta hektar — lumbung padi kita.
> Tapi angkanya terus turun. Tiap tahun, ribuan hektar beralih fungsi.
> Pertanyaan untuk Anda: kalau sawah terus menyusut, dari mana kita makan di tahun 2045?
> Penduduk bertambah, lahan berkurang. Menuju Indonesia Emas — atau menuju lapar?

## Captions (condensed, per beat)
| start | text | act |
|---|---|---|
| 0 | Dua puluh tahun lalu, ini sawah. | 1 |
| 5 | Sekarang? Lihat sendiri. | 1 |
| 10 | Hijau → abu-abu: sawah jadi rumah & pabrik. | 1 |
| 17 | Bagaimana saya tahu? Dari satelit. | 2 |
| 24 | Citra satelit itu angka, bukan foto. | 2 |
| 33 | Sawah khas: tergenang → menghijau → panen. Radar menangkapnya. | 2 |
| 43 | Ribuan citra → model → peta sawah Jawa. | 2 |
| 52 | Sawah Jawa kini ± 2,28 juta ha. | 3 |
| 60 | Tapi terus menyusut tiap tahun. | 3 |
| 68 | 2045: penduduk naik, sawah turun. | 4 |
| 76 | Dari mana kita makan? | 4 |

## Visual plan (assets)
- **Act 1–2 background:** `urban_sprawl.mp4` (have) — Bekasi–Karawang time-lapse. Act 2 can zoom/annotate over it.
- **Act 3–4 background:** **NEW — `paddy_java.png`** (Java paddy map, green=paddy). Generate from `paddy_classification_gee.py` (add a thumbnail export) or from the S1 repo output.
- **Optional Act 2 explainer:** a short "pixel grid → spectral curve → flood/grow/harvest" motif (Remotion-animated) — higher effort; or keep it imagery + captions.
- **End card:** "Mana buktinya? Ada di citra satelit. @jalmiburung 🛰️"

## Post copy (tweet body — no link)
> Dua puluh tahun lalu, ini sawah. Sekarang lihat sendiri.
>
> Saya petakan sawah Jawa dari satelit — kini ± 2,28 juta ha, dan terus menyusut.
>
> Kalau begini terus, dari mana kita makan di 2045? 🌾

## First reply (method + data + link)
> Caranya: radar Sentinel-1 menangkap pola khas sawah (genangan → tumbuh → panen), dilatih dengan 21.000+ titik survei lapangan, akurasi 95%. Data nasional (BPS): lahan baku sawah 7,46 → 7,38 juta ha (2019–2024), mayoritas susut di Jawa. Detail + skrip: [LINK]

(Verify 2,28 juta ha & BPS figures before posting — see [[Sawah Decline Java — Results]].)

## Production note
This is a bigger Remotion build than v1: two background media (time-lapse for Act 1–2, paddy map for Act 3–4) across `Sequence`s, longer duration. v1 composition still exists for the short cut.
