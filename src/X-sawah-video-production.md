---
title: X Video Production — "Dulu ini sawah"
type: note
date: 2026-06-27
ai-first: true
tags: [social-media, x-twitter, video, production, sawah, jalmiburung]
account: "@jalmiburung"
stack: GEE (timelapse) + ElevenLabs (narration) + moviepy (compositing)
---
# X Video Production — "Dulu ini sawah"

## For future Claude

Step-by-step to produce the urban-sprawl / sawah-loss X video for @jalmiburung. Visual = Landsat 1985→2025 time-lapse of sawah turning to city (from `gee_urban_sprawl_timelapse.py`); narration in his voice (ID, "Anda", ngedumel); compositing via `make_x_video.py` (moviepy, no Remotion needed). Backed by today's sawah analysis ([[Sawah Decline Java — Results]]) + his S1 map ([[PUPR]]). Format rules from [[X-insights]]: hook in 2s, captions burned in, link in FIRST REPLY.

## Pipeline (3 steps)
1. **GEE time-lapse** → run `python social-media/gee_urban_sprawl_timelapse.py` (it calls `render_local()` → `urban_sprawl.mp4` with year counter). Pick a recognizable city in the script (`center`), e.g. Bandung Selatan / Bekasi–Karawang.
2. **Narration** → paste the narration below into ElevenLabs (Indonesian voice), export `narration.mp3` into `social-media/`.
3. **Composite** → `python social-media/make_x_video.py` → `sawah_video.mp4` (square, captions + narration). Post it.

## Final narration (≈42 s, ID — paste into ElevenLabs)
> Dua puluh tahun lalu, ini sawah.
> Sekarang? Lihat sendiri.
> Setiap petak hijau yang berubah jadi abu-abu — lumbung pangan yang berganti jadi perumahan.
> Kita bicara swasembada beras, tapi mengubah sawah menjadi rumah atau pabrik.
> Saya memetakan sawah Jawa dengan satelit. Datanya jelas: luas sawah menyusut, pelan tapi pasti.
> Ini bukan tuduhan. Ini adalah fakta. Citra gratis, sejak 1985. Data satelit tidak berbohong.

(ElevenLabs tips: Indonesian-capable voice, Stability ~50, Style ~30, speak calmly — it's a narration, not an ad.)

## Timed captions (burned in by make_x_video.py, for muted viewers)
| start | text |
|---|---|
| 0.0 | Dua puluh tahun lalu, ini sawah. |
| 4.5 | Sekarang? Lihat sendiri. |
| 9.0 | Hijau → abu-abu: sawah jadi perumahan. |
| 17.0 | Swasembada beras, tapi sawahnya dikubur aspal. |
| 26.0 | Saya petakan sawah Jawa dari satelit. |
| 31.0 | Kita menyusut — pelan tapi pasti. |
| 36.0 | Citra gratis, sejak 1985. Satelit tak bohong. |

## Post copy (tweet body — NO link here)
> Dua puluh tahun lalu, ini sawah. Sekarang lihat sendiri.
>
> Kita bicara swasembada beras, sambil mengubur lumbung pangan di bawah aspal.
>
> Satelit merekam semuanya — gratis, sejak 1985. 🛰️🌾

## First reply (the link + credibility + data)
> Citra Landsat (gratis) saya rakit di Google Earth Engine. Datanya: sawah/lahan pertanian Jawa terus menyusut sejak 2000-an (BPS: lahan baku sawah nasional 7,46 → 7,38 juta ha, 2019–2024), mayoritas di Jawa karena alih fungsi ke perumahan & infrastruktur. Skrip + cara buatnya: [LINK]

(Verify the BPS figures before posting — see [[Sawah Decline Java — Results]] §5.)

## Checklist
- [ ] Square 1080×1080 (or vertical 1080×1350), captions burned in
- [ ] Hook visible in first 2 s
- [ ] ≤ 45 s
- [ ] Link in FIRST REPLY only
- [ ] Post 12:00 or 20:00 WIB; engage 20 min after
- [ ] BPS numbers verified
