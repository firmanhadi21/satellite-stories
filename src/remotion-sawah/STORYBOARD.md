# Storyboard — "Dulu ini sawah" (Remotion, 1080×1080, 30 fps)

Total ≈ 44 s = 1320 frames (auto-set from narration + 2 s end card). The base is an
overhead time-lapse, so motion comes from a **continuous virtual camera** (scale/translate
via `interpolate`) plus a **punch-in on the irony beat**. Captions are `Sequence`s on top.

## Shot list

| # | Frames (s) | Visual | Virtual camera (Remotion) | Text / overlay | Narration beat |
|---|---|---|---|---|---|
| 1 **Cold open** | 0–120 (0–4s) | Still 1985 frame, lush green | slow push-in `scale 1.05→1.10` | Title caption fades in (f8); year badge **1985** top-left | "Dua puluh tahun lalu, ini sawah." |
| 2 **Reveal** | 120–270 (4–9s) | Time-lapse starts; year counter ticks | continue `scale →1.12` | caption swap (crossfade) | "Sekarang? Lihat sendiri." |
| 3 **Transformation** | 270–510 (9–17s) | Green → grey spreading | gentle pan `x 0→−4%` toward change | caption "Hijau → abu-abu…" | "...lumbung pangan jadi perumahan." |
| 4 **The turn (punch-in)** | 510–780 (17–26s) | Lock on a parcel converting to housing | **punch-in `scale 1.12→1.30`**, vignette fades in | caption "Swasembada beras, tapi sawahnya dikubur aspal." | the irony — held beat |
| 5 **Credibility** | 780–930 (26–31s) | Pull back to full extent; faint crosshair/corner ticks (satellite-UI feel) | `scale 1.30→1.10`, vignette out | caption "Saya petakan sawah Jawa dari satelit." | "...Datanya jelas." |
| 6 **Proof** | 930–1260 (31–42s) | Time-lapse lands on 2025; year badge pulses | slow drift `scale 1.10→1.12` | caption "Citra gratis, sejak 1985. Satelit tak bohong." | proof / disarm |
| 7 **End card** | 1260–1320 (42–44s) | Video dims to ~20%, near-black | hold | centered text **springs** in: "Mana datanya?\nAda di langit.\n@jalmiburung 🛰️" | (silence / music tail) |

## Camera keyframes (one transform on the video layer)
```ts
const frame = useCurrentFrame();
// scale: push-in, punch-in at the irony, pull back, settle
const scale = interpolate(
  frame,
  [0, 120, 510, 780, 930, 1260],
  [1.05, 1.10, 1.12, 1.30, 1.10, 1.12],
  {extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic)}
);
// subtle pan toward the area of biggest change (kept small; scale>1 gives headroom)
const panX = interpolate(frame, [270, 780], [0, -0.04], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
// style on the <OffthreadVideo> wrapper:
transform: `scale(${scale}) translateX(${panX * 100}%)`
```

## Vignette (focus the punch-in)
```ts
const vig = interpolate(frame, [510, 640, 780, 930], [0, 0.5, 0.5, 0], {extrapolateLeft:"clamp", extrapolateRight:"clamp"});
// AbsoluteFill with radial gradient, opacity = vig:
background: "radial-gradient(circle at 50% 45%, transparent 45%, rgba(0,0,0,0.85) 100%)"
```

## End-card dim + spring
```ts
const videoOpacity = interpolate(frame, [1255, 1275], [1, 0.2], {extrapolateLeft:"clamp", extrapolateRight:"clamp"});
const pop = spring({frame: frame - 1260, fps, config: {damping: 14}});  // scale text in
```

## Year badge (optional — only if GEE export has NO burned-in year)
```ts
const year = Math.round(interpolate(frame, [0, 1260], [1985, 2025], {extrapolateRight:"clamp"}));
// render `${year}` top-left, monospace; pulse near the end via spring(frame-930)
```
If the GEE `render_local()` already burns the year, skip this to avoid double labels
(export without the label in that case).

## Editing rhythm
- Caption changes land **on the narration**, not evenly — keep the `CAPTIONS` start times synced to the ElevenLabs audio (check in `npm run studio`).
- The single most important cut is the **punch-in at f510 (17s)** — it must hit exactly on "Swasembada beras…". That contradiction is the emotional peak.
- Keep all moves **slow and few**; the land changing is the spectacle, the camera only guides the eye.

## Transitions (optional polish)
- Crossfade between captions: already handled by per-caption opacity fade.
- For a film-grain/letterbox vibe, add thin top/bottom bars (8% height) — but square+full-bleed usually performs better on X.
- For a fancier end-card wipe, `@remotion/transitions` `TransitionSeries` with `fade()` — extra dep, optional.
