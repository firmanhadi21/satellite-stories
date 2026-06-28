# remotion-sawah — "Dulu ini sawah" X video

Remotion project that composites the Landsat time-lapse + ElevenLabs narration +
animated captions + end card into a square X-ready video. Companion to the
Python compositor (`../make_x_video.py`); use whichever you prefer.

## Assets (put these in `public/`)
- `public/urban_sprawl.mp4` — from `../gee_urban_sprawl_timelapse.py` (run `render_local()`)
- `public/narration.mp3`    — ElevenLabs export (narration text in `../X-sawah-video-production.md`)

> Tip: export the GEE time-lapse so it's ROUGHLY the narration length (~40s).
> In `gee_urban_sprawl_timelapse.py` set `framesPerSecond` lower (≈1) for ~40s.
> The composition also `<Loop>`s the video, so shorter clips still fill the duration.

## Run
```bash
cd social-media/remotion-sawah
npm install
mkdir -p public out
# copy urban_sprawl.mp4 and narration.mp3 into public/
npm run studio      # preview/tweak live at localhost:3000
npm run render      # -> out/sawah_video.mp4
```

## Customize
- **Aspect ratio:** `src/Root.tsx` → `height={1080}` (square) or `1350` (vertical 4:5).
- **Captions / timings:** `src/SawahVideo.tsx` → `CAPTIONS` array (seconds).
- **Duration:** auto-set from `narration.mp3` length + 2s end card (via `calculateMetadata`).
- **End card text:** `END_CARD` in `src/SawahVideo.tsx`.

## Notes
- Duration is derived from the narration automatically — no manual frame math.
- If `npm install` is slow, `npx create-video@latest` first then drop in `src/` also works.
- Requires Node 18+ and a Chromium (Remotion installs one).
