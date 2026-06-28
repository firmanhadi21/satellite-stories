# Satellite Stories 🛰️

Turn satellite remote-sensing analysis into short, narrated explainer videos for social media.
Sentinel-1/2 + Landsat in **Google Earth Engine** → **ElevenLabs** voiceover → **Remotion** video.

Built by [@jalmiburung](https://x.com/jalmiburung). Two worked examples:

1. **Sawah decline in Java** — Sentinel-1 built-up time-lapse + paddy mapping + the food-security question.
2. **Nickel-mining destruction in Konawe** — NDVI loss time-lapse + **SIRAD** radar change map.

---

## What it does

Each video follows a 3-act structure: **the change** (a satellite time-lapse) → **how we measure it** (the method, animated) → **the current state + a provocation**. The pipeline has three stages:

| Stage | Tool | Output |
|---|---|---|
| A. Remote-sensing analysis | Google Earth Engine (Python) | time-lapse `.mp4`, index/SIRAD `.png` |
| B. Narration | ElevenLabs API | `narration.mp3` |
| C. Video assembly | Remotion (React/TypeScript) | final `.mp4` (square, captions, music) |

---

## Prerequisites

- **Python** 3.10+ and **Node** 18+
- A **Google Earth Engine** account with a **service-account** key (JSON)
- An **ElevenLabs** API key (for narration)
- *(optional)* A **Planet** API key with PlanetScope access (Education/Research license works)

---

## 1. Setup

```bash
git clone https://github.com/<you>/satellite-stories.git
cd satellite-stories

# Python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Remotion (Node)
cd src/remotion-sawah && npm install && cd ../..
```

### Credentials
Copy the templates in `Credentials/` and fill in your keys (this folder is git-ignored):

```bash
cp Credentials/gee.txt.example          Credentials/gee.txt
cp Credentials/elevenlabs.txt.example   Credentials/elevenlabs.txt
cp Credentials/planet.txt.example       Credentials/planet.txt     # optional
# put your GEE service-account JSON at:  Credentials/ee-geodetic.json
```

- `gee.txt` — project id, service-account email, key path (see example)
- `elevenlabs.txt` — `ELEVENLABS_API_KEY=...` and `ELEVENLABS_VOICE_ID=...`
- `planet.txt` — your Planet API key (one line)

All scripts read `../Credentials` relative to themselves, so keep the folder layout intact.

---

## 2. Stage A — Remote-sensing analysis (GEE)

All scripts live in `src/`. Run them from the repo root with the venv active.

| Script | What it makes |
|---|---|
| `src/gee_urban_sprawl_timelapse.py` | Sentinel-1 VV built-up time-lapse (red = buildings, grows monotonically) |
| `src/gee_method_stills.py` | NDBI / NDVI / false-color + S1 built-up vs sawah stills (method scenes) |
| `src/gee_konawe_mining_timelapse.py` | Landsat NDVI-loss time-lapse + Hansen forest-loss hectares |
| `src/gee_konawe_sirad.py` | **SIRAD** radar change composite (R/G/B = 3 periods of mean VH) |
| `src/gee_konawe_sirad_map.py` | SIRAD as a **map** (north arrow, scale, coordinates, legend, infographic) |

Each writes its output next to itself **and auto-copies into `src/remotion-sawah/public/`**.

```bash
python src/gee_urban_sprawl_timelapse.py     # -> urban_sprawl.mp4
python src/gee_method_stills.py              # -> ndbi.png, ndvi.png, s1_builtup.png, s1_sawah.png
```

> **SIRAD** = *Sistema de Indicação Radar de Desmatamento* (Juan Doblas, Instituto Socioambiental),
> with the Refined Lee speckle filter by Guido Lemoine. Sentinel-1 multitemporal change detection,
> ported to Python here. See `src/gee_konawe_sirad.py`.

---

## 3. Stage B — Narration (ElevenLabs)

```bash
python src/make_narration.py            # sawah video voiceover -> narration.mp3
python src/make_konawe_narration.py     # konawe video voiceover -> narration_konawe.mp3
```

Edit the `NARRATION = (...)` block at the top of each to change the script. Both auto-copy the
`.mp3` into `src/remotion-sawah/public/`. List voices with `python src/make_narration.py --list`.

---

## 4. Stage C — Video assembly (Remotion)

```bash
cd src/remotion-sawah
npm run studio       # live preview at localhost:3000 (tweak captions/timings visually)
npm run render       # -> out/sawah_video.mp4
```

- The composition (`src/SawahVideo.tsx`) auto-sizes its duration to the narration length.
- Caption/scene timings are in `src/SawahVideo.tsx` (`CAPTIONS` array + `<Sequence>` start times).
- The animated method scenes are in `src/MethodExplainer.tsx`.

---

## 5. Reproduce the sawah video end-to-end

```bash
source .venv/bin/activate
python src/gee_urban_sprawl_timelapse.py
python src/gee_method_stills.py
python src/make_narration.py
cp ~/path/to/your_paddy_map.png src/remotion-sawah/public/paddy_java.png   # Act-3 result map
cd src/remotion-sawah && npm run render
```

## 6. Reproduce the Konawe mining video

```bash
python src/gee_konawe_mining_timelapse.py    # NDVI-loss time-lapse + forest-loss ha
python src/gee_konawe_sirad.py               # SIRAD radar change composite
python src/gee_konawe_sirad_map.py           # SIRAD cartographic figure + infographic
python src/make_konawe_narration.py          # narration_konawe.mp3
# then build a Konawe composition in Remotion (same pattern as SawahVideo)
```

PlanetScope AOI + search (optional, needs Planet key):
```bash
python src/planet_konawe_search.py           # search PSScene over konawe_aoi.geojson
```

---

## 7. Bonus — Java sawah-decline analysis

Standalone remote-sensing scripts (not part of a video) that ask: *is paddy area in Java
shrinking over decades, and where most?* Same credential setup; run from the repo root.

| Script | What it does |
|---|---|
| `src/paddy_classification_gee.py` | Sentinel-1 + Sentinel-2 Random-Forest paddy map from field/training points (needs `src/training_points_random_java.csv`) |
| `src/paddy_decadal_trend_gee.py` | MODIS cropland-area trend over Java, 2001–2023 (chart + slope) |
| `src/paddy_decadal_trend_glcfcs30d.py` | GLC-FCS30D 30 m paddy-proxy trend, 1985–2022 |
| `src/paddy_loss_by_province.py` | per-province sawah-loss ranking (CSV + chart) |

> The training CSV (`training_points_random_java.csv`) is **not** committed (data stays private).
> Drop your own labelled points (`tanggal;lintang;bujur;paddy`) into `src/` to run the classifier.
> Key finding from these: global land-cover products *disagree* on the trend, so validate against
> BPS *Lahan Baku Sawah* — i.e. "mana datanya?".

## Customizing

- **Area of interest** — edit `center` / `buffer` in the GEE scripts (or `konawe_aoi.geojson`).
- **Dates / periods** — `YEARS` (time-lapses) and `DATES` (SIRAD) at the top of each script.
- **Narration** — the `NARRATION` block in the `make_*_narration.py` scripts.
- **Captions & timing** — `CAPTIONS` in `src/SawahVideo.tsx` (sync to the audio in `npm run studio`).

---

## Credits & data

- **SIRAD** — Juan Doblas, Instituto Socioambiental.
- **Refined Lee** speckle filter — Guido Lemoine.
- **Sentinel-1/2** © ESA / Copernicus; **Landsat** © USGS/NASA; **Hansen Global Forest Change** (UMD).
- Processing: **Google Earth Engine**. Video: **Remotion**. Voice: **ElevenLabs**.

## License
MIT — see `LICENSE`. (Note: imagery and third-party algorithms retain their own licenses/terms.)
