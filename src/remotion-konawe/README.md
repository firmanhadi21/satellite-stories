# remotion-konawe — "Konawe: hutan jadi tambang" video

Standalone Remotion project for the Konawe nickel-mining destruction video.
Acts: NDVI-loss time-lapse → NDVI/SIRAD method → SIRAD map result (with infographic)
→ nickel-vs-environment provocation.

## Assets (put in `public/` — the GEE/narration scripts auto-copy them here)
- `konawe_timelapse.mp4`  — `../gee_konawe_mining_timelapse.py` (NDVI loss)
- `sirad_konawe.png`      — `../gee_konawe_sirad.py` (radar change composite)
- `sirad_konawe_map.png`  — `../gee_konawe_sirad_map.py` (map + infographic)
- `narration_konawe.mp3`  — `../make_konawe_narration.py`

## Run
```bash
cd social-media/remotion-konawe
npm install
mkdir -p public out
npm run studio      # preview at localhost:3000
npm run render      # -> out/konawe_video.mp4
```

## Sync timings
Beat times in `src/KonaweVideo.tsx` (`CAPTIONS` + `<Sequence>` starts) are estimates.
Open studio, read where each narration line begins, and adjust the `S(...)` values.
