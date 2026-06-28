# Credentials

This folder holds your **private keys** — it is git-ignored (only the `*.example`
files are committed). Copy each example, drop the `.example`, and fill in your values.

| File | What it is |
|---|---|
| `gee.txt` | Earth Engine project id + service-account email + key path |
| `ee-geodetic.json` | your Earth Engine **service-account key** (download from Google Cloud) |
| `elevenlabs.txt` | ElevenLabs API key + voice id |
| `planet.txt` | Planet API key (optional, for PlanetScope) |

```bash
cp gee.txt.example gee.txt
cp elevenlabs.txt.example elevenlabs.txt
cp planet.txt.example planet.txt
# then place your service-account JSON here as ee-geodetic.json
```

Environment variables override the files if set: `GEE_*`, `ELEVENLABS_API_KEY`,
`ELEVENLABS_VOICE_ID`, `PL_API_KEY`.

**Never commit real keys.** If one leaks, rotate it immediately.
