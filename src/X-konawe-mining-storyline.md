---
title: X Video Storyline — Konawe Nickel Mining (balanced)
type: note
date: 2026-06-27
ai-first: true
tags: [social-media, x-twitter, video, storyline, mining, konawe, nickel, deforestation, jalmiburung]
account: "@jalmiburung"
length: "~90s, 3 perspectives + closing question"
---
# X Video Storyline — Konawe Nickel Mining (balanced)

## For future Claude

Second video in the "satellite tells the truth" series for @jalmiburung — nickel-mining in Konawe Utara (Sulawesi Tenggara), but framed as a **balanced dilemma, not a one-sided takedown**. Flow: (1) the damage — NDVI-loss time-lapse + SIRAD radar method + map result; (2) the economy — jobs, income, nickel = EV-battery feedstock; (3) the true cost — forest/river/sea + lost ecosystem services that "never enter the balance sheet"; (4) closing question — chase revenue while ignoring the cost? Standalone Remotion project `remotion-konawe`. AOI: 122.174, -3.528 (12 km box). Forest loss ≈ 6,093 ha (Hansen 2001-2024). Econ figures are qualitative — drop verified numbers into the Neraca scene's EKONOMI array if available.

## Scripts / assets
- `gee_konawe_mining_timelapse.py` → `konawe_timelapse.mp4` (NDVI loss) + prints Hansen forest-loss ha (≈6,093)
- `gee_konawe_sirad.py` → `sirad_konawe.png` (SIRAD radar change composite, R/G/B = 3 periods VH)
- `gee_konawe_sirad_map.py` → `sirad_konawe_map.png` (cartographic: north/scale/coords/legend + loss infographic)
- `make_konawe_narration.py` → `narration_konawe.mp3`
- `remotion-konawe/` → the video project (`src/KonaweVideo.tsx`: timelapse → NDVI → SIRAD → map → Neraca → question)

## Narration (≈90s, ID — source: make_konawe_narration.py)
> Sepuluh tahun lalu, ini hutan. Sekarang? Lihat sendiri.
> Hijau berubah jadi merah — hutan dikupas menjadi tambang nikel.
> Bagaimana saya tahu? Dari satelit. Tiap tahun ia mengukur kehijauan — indeks NDVI.
> Hutan rapat nilainya tinggi; tanah terbuka, rendah. Ketika hutan dibuka, NDVI anjlok.
> Radar Sentinel-1, lewat metode SIRAD, bahkan mencatat kapan tiap petak dibuka.
> Hasilnya: ribuan hektar hutan lenyap.
> Tapi mari adil. Tambang ini juga memberi: lapangan kerja, dan pendapatan bagi daerah dan negara.
> Nikel adalah bahan baku baterai dunia — denyut transisi energi.
> Hanya saja, pembangunan sejati menghitung ongkosnya.
> Hutan yang hilang, sungai yang keruh, laut yang tercemar.
> Jasa ekosistem — air bersih, ikan, udara, penyerap karbon — ikut lenyap, dan tak pernah masuk neraca.
> Maka pertanyaannya untuk kita: haruskah kita kejar pendapatan, sambil menutup mata pada kerusakan dan ongkos lingkungannya?

## Scenes (KonaweVideo.tsx — fractions of the timeline)
| frac | scene |
|---|---|
| 0–18% | NDVI-loss time-lapse (forest green → bare red) |
| 18–30% | NDVI scale explainer (hutan tinggi → tanah rendah) |
| 30–42% | SIRAD radar reveal (`sirad_konawe.png`; colour = when cleared) |
| 42–56% | SIRAD map result (`sirad_konawe_map.png`; ribuan hektar lenyap) |
| 56–85% | **Neraca pembangunan** — PENDAPATAN (kerja, pendapatan, baterai) vs ONGKOS (hutan 6.093 ha, sungai, laut, jasa ekosistem) |
| 85–end | **Closing question** — "haruskah kita kejar pendapatan…?" |

## Captions (bottom, Act 1 + result; method/Neraca/question carry own text)
- "Sepuluh tahun lalu, ini hutan."
- "Hijau → merah: hutan jadi tambang nikel."
- "Ribuan hektar hutan lenyap."

## Post copy (tweet body — no link)
> Sepuluh tahun lalu, ini hutan Konawe. Sekarang lihat sendiri — kini tambang nikel.
>
> Nikel memberi lapangan kerja & pendapatan. Tapi hutan, sungai, laut, dan jasa ekosistem ikut hilang.
>
> Haruskah kita kejar pendapatan sambil mengabaikan ongkosnya? 🛰️

## First reply (method + data + link)
> Caranya: NDVI dari satelit (kehijauan turun saat hutan dibuka) + radar Sentinel-1 (metode SIRAD) yang mencatat KAPAN tiap petak dibuka. Kehilangan tutupan pohon di AOI ini ± 6.093 ha (Hansen GFC 2001–2024). Skrip + cara reproduksinya: [LINK]

(Verify the forest-loss number against Global Forest Watch; add verified jobs/revenue figures if you cite them.)

## Notes
- **Balanced on purpose** — damage + economy + true cost, ending on a question, not a verdict. Stronger and harder to dismiss than a one-sided clip.
- Econ side is qualitative; real figures (BPS Sultra / ESDM / company reports) go into the `EKONOMI` array in `KonaweVideo.tsx` and the narration.
- NDVI loss is monotonic (cleared forest stays bare); SIRAD adds the "when" via radar.
- Same "mana buktinya? ada di citra satelit" sign-off end card.
