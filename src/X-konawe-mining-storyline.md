---
title: X Video Storyline — Konawe Nickel Mining Destruction
type: note
date: 2026-06-27
ai-first: true
tags: [social-media, x-twitter, video, storyline, mining, konawe, nickel, deforestation, jalmiburung]
account: "@jalmiburung"
length: "~85s, 3 acts + provocation"
---
# X Video Storyline — Konawe Nickel Mining

## For future Claude

Second video in the "satellite tells the truth" series for @jalmiburung — same 3-act logic as the sawah video ([[X-sawah-video-storyline-v2]]), pointed at nickel-mining forest destruction in Konawe Utara (Sulawesi Tenggara). Act 1 = NDVI-loss time-lapse (forest green → bare brown/red, monotonic); Act 2 = how NDVI detects clearing; Act 3 = forest-loss hectares from Hansen GFC (printed by the GEE script); Act 4 = nickel/EV-boom vs environment provocation. AOI: Konawe Utara nickel belt (122.05, -3.55). Reuses the remotion-sawah project pattern.

## Scripts / assets
- `gee_konawe_mining_timelapse.py` → `konawe_timelapse.mp4` (NDVI loss, ~17s) + prints forest-loss ha (Hansen)
- `make_konawe_narration.py` → `narration_konawe.mp3`
- Remotion: a `KonaweVideo` composition (to build) reusing PixelGrid/Phenology-style scenes; method scene = forest-loss focused
- Method stills (optional): a "hutan vs tambang" NDVI side-by-side (can reuse gee_method_stills pattern for the Konawe AOI)

## Narration (≈85s, ID — in make_konawe_narration.py)
> Sepuluh tahun lalu, ini hutan. Sekarang? Lihat sendiri.
> Hijau berubah jadi cokelat — hutan dikupas menjadi tambang nikel.
> Bagaimana saya tahu? Bukan dari katanya. Dari satelit.
> Tiap tahun satelit mengukur kehijauan — indeks NDVI. Hutan rapat tinggi; tanah terbuka rendah.
> Ketika hutan dibuka untuk tambang, NDVI anjlok. Satelit mencatatnya, petak demi petak.
> Saya petakan kehilangannya. Di blok ini saja, ribuan hektar hutan lenyap dalam sepuluh tahun.
> Kita bangga menjadi raja nikel dunia.
> Tapi pertanyaan untuk Anda: berapa hutan dan sungai yang kita korbankan untuk itu?
> Baterai mobil listrik menyala di sana — air dan hutan padam di sini. Kemajuan, untuk siapa?

## Captions (per beat — retime to audio in studio)
| beat | text |
|---|---|
| Act1 | "Sepuluh tahun lalu, ini hutan." |
| Act1 | "Hijau → cokelat: hutan jadi tambang nikel." |
| Act2 | "NDVI: hutan tinggi, tanah terbuka rendah." |
| Act2 | "Hutan dibuka → NDVI anjlok. Satelit mencatat." |
| Act3 | "Ribuan hektar hutan lenyap di Konawe." |
| Act4 | "Raja nikel dunia — tapi berapa harganya?" |
| Act4 | "Maju untuk siapa, kalau air & hutan hilang?" |

## Post copy (tweet body — no link)
> Sepuluh tahun lalu, ini hutan Konawe. Sekarang lihat sendiri.
>
> Kita raja nikel dunia — tapi berapa hutan dan sungai yang kita korbankan? 🛰️🌳

## First reply (method + data + link)
> Caranya: satelit mengukur NDVI (indeks kehijauan) tiap tahun. Hutan dibuka → NDVI anjlok. Kehilangan tutupan pohon di blok ini ± [X ha — dari skrip, Hansen GFC 2001-2023]. Skrip + cara reproduksinya: [LINK]

(Use the forest-loss number the GEE script prints; verify against Global Forest Watch.)

## Notes
- Method clean & monotonic: forest cleared for nickel stays bare, so NDVI loss doesn't flicker (unlike NDBI built-up).
- Optional stronger Act-1: add river/coast sediment (red plumes) — a second AOI over the river mouth.
- Tie-in: same "mana buktinya? ada di citra satelit" signature/end card.
