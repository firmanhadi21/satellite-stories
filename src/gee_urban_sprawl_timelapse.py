#!/usr/bin/env python3
"""
URBAN SPRAWL TIME-LAPSE  ·  Landsat 5/7/8/9  ·  1985-2025
Earth Engine Python API. For X video #1 "Dulu ini sawah" (@jalmiburung).
See [[X-video-scripts]].

Install:
    pip install earthengine-api                       # core
    pip install requests pillow imageio imageio-ffmpeg numpy   # for local render
"""

import os
import ee

# --- 0. CONNECT (reads Credentials/gee.txt + service-account key) ------
# Credentials live in the vault's Credentials/ folder:
#   Credentials/gee.txt           -> config (project id, SA email, key path)
#   Credentials/ee-geodetic.json  -> service-account private key
CRED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "Credentials")

def _load_config(path):
    cfg = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    return cfg

cfg = _load_config(os.path.join(CRED_DIR, "gee.txt"))
PROJECT = cfg.get("GEE_PROJECT_ID", "ee-geodeticengineeringundip")
SA_EMAIL = cfg.get("GEE_SERVICE_ACCOUNT_EMAIL")

# Prefer the key file sitting next to gee.txt; fall back to the path in gee.txt.
KEY_FILE = os.path.join(CRED_DIR, "ee-geodetic.json")
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser(cfg.get("GEE_SERVICE_ACCOUNT_KEY_FILE", ""))

creds = ee.ServiceAccountCredentials(SA_EMAIL, KEY_FILE)
ee.Initialize(creds, project=PROJECT)
print(f"Connected to GEE project: {PROJECT}")

# Interactive alternative (no service account):
#   ee.Authenticate(); ee.Initialize(project=PROJECT)

# --- 1. AREA OF INTEREST — change the point to your city ---------------
# Presets (lon, lat):
#   Bandung Selatan / Bojongsoang : 107.6386, -6.9750   (sawah -> perumahan)
#   Bekasi-Cikarang (industri)    : 107.1500, -6.2700
#   Karawang (sawah -> industri)  : 107.3000, -6.3200
#   Serpong / BSD (Jabodetabek)   : 106.6700, -6.3000
center = ee.Geometry.Point([107.22, -6.31])         # Bekasi–Karawang corridor (sawah -> industri/perumahan)
aoi = center.buffer(9000).bounds()                  # ~18 km square box (captures the corridor)

START_YEAR, END_YEAR = 1988, 2025   # Landsat coverage over Indonesia is reliable from ~1988

# --- 2. CLOUD / SHADOW MASK (Landsat Collection 2 L2, QA_PIXEL) --------
def mask_l2(img):
    qa = img.select("QA_PIXEL")
    m = (qa.bitwiseAnd(1 << 1).eq(0)        # dilated cloud
         .And(qa.bitwiseAnd(1 << 3).eq(0))  # cloud
         .And(qa.bitwiseAnd(1 << 4).eq(0))  # cloud shadow
         .And(qa.bitwiseAnd(1 << 2).eq(0))) # cirrus (L8/9)
    return img.updateMask(m)

# --- 3. SCALE TO REFLECTANCE + RENAME TO COMMON BANDS -----------------
def prep(img, era):
    img = mask_l2(img)
    if era == "old":   # L4/5/7: blue B1 green B2 red B3 nir B4 swir1 B5 swir2 B7
        b = img.select(["SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B7"],
                       ["blue", "green", "red", "nir", "swir1", "swir2"])
    else:              # L8/9:   blue B2 green B3 red B4 nir B5 swir1 B6 swir2 B7
        b = img.select(["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7"],
                       ["blue", "green", "red", "nir", "swir1", "swir2"])
    return (b.multiply(0.0000275).add(-0.2)           # C2 L2 scale + offset
            .copyProperties(img, ["system:time_start"]))

# --- 4. SENTINEL-1 GRD (VV) — built-up is bright & only INCREASES -----
# Radar double-bounce off buildings = strong, stable return (unlike noisy NDBI).
s1 = (ee.ImageCollection("COPERNICUS/S1_GRD")
      .filterBounds(aoi)
      .filter(ee.Filter.eq("instrumentMode", "IW"))
      .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
      .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
      .select("VV"))

# --- 5. VISUALIZATION -------------------------------------------------
# Sentinel-1 VV (dB): water ~ -22, vegetation ~ -12, built-up ~ -6..0.
# Bright RED = buildings (strong radar return). Built-up only GROWS over time.
VV_VIS = {"min": -20, "max": 0,
          "palette": ["08081f", "1f3b73", "3a7ca5", "9bc24a", "ffd24a", "ff7043", "d7191c"]}

# --- 6. ONE ANNUAL COMPOSITE PER YEAR (median) -> RGB FRAMES ----------
def annual_rgb(year):
    annual = (s1.filterDate(f"{year}-01-01", f"{year}-12-31").median()
              .focal_median(30, "circle", "meters"))      # despeckle
    return annual.visualize(**VV_VIS).clip(aoi).set("year", year)

YEARS = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]   # S1 era; ~17s
frames = ee.ImageCollection([annual_rgb(y) for y in YEARS])

# --- 7. QUICK PREVIEW (animation URL, open in browser) ---------------
print("Animation preview:")
print(frames.getVideoThumbURL({
    "dimensions": 600, "framesPerSecond": 4, "region": aoi, "crs": "EPSG:3857"
}))

# --- 8a. SERVER-SIDE EXPORT to Google Drive --------------------------
def export_to_drive():
    task = ee.batch.Export.video.toDrive(
        collection=frames,
        description="urban_sprawl_timelapse",
        dimensions=1080,          # square output (AOI is square); good for X
        framesPerSecond=4,        # ~10 s for 1985-2025; lower = slower
        region=aoi,
        crs="EPSG:3857",
        folder="earthengine",
    )
    task.start()
    print("Export started:", task.id, task.status()["state"])
    return task

# --- 8b. LOCAL RENDER with burned-in year counter --------------------
def render_local(out_path=None, dimensions=1080, target_seconds=17):
    """Download each yearly frame, draw the year, stitch to MP4 locally."""
    if out_path is None:                                  # write next to this script
        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "urban_sprawl.mp4")
    import io
    import time
    import shutil
    import requests
    import numpy as np
    import imageio.v2 as imageio
    from PIL import Image, ImageDraw, ImageFont

    fsize = dimensions // 8                       # big, legible year (~135 px at 1080)
    font = None
    for p in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc",
              "/Library/Fonts/Arial.ttf",
              "DejaVuSans-Bold.ttf"]:
        try:
            font = ImageFont.truetype(p, fsize)
            break
        except OSError:
            continue
    if font is None:                              # last resort (Pillow >=10.1 scales it)
        try:
            font = ImageFont.load_default(size=fsize)
        except TypeError:
            font = ImageFont.load_default()

    def fetch_year(y, attempts=5):
        last = None
        for a in range(attempts):
            try:
                url = annual_rgb(y).getThumbURL(
                    {"region": aoi, "dimensions": dimensions, "format": "png", "crs": "EPSG:3857"})
                r = requests.get(url, timeout=180)
                r.raise_for_status()
                png = Image.open(io.BytesIO(r.content)).convert("RGB")
                d = ImageDraw.Draw(png)
                label = str(y)
                m, pad = dimensions // 30, dimensions // 70
                bb = d.textbbox((0, 0), label, font=font, stroke_width=5)
                tw, th = bb[2] - bb[0], bb[3] - bb[1]
                d.rectangle([m - pad, m - pad, m + tw + pad, m + th + pad * 2],
                            fill=(0, 0, 0))                 # dark plate behind the year
                d.text((m - bb[0], m - bb[1]), label, font=font,
                       fill="white", stroke_width=5, stroke_fill="black")
                return np.array(png)
            except Exception as e:                 # GEE/network hiccup -> back off, retry
                last = e
                time.sleep(3 * (a + 1))
        print(f"  year {y} FAILED after {attempts} tries: {last}")
        return None

    imgs = []
    for y in YEARS:
        arr = fetch_year(y)
        if arr is not None:
            imgs.append(arr)
            print("frame", y, "ok")

    if not imgs:
        raise SystemExit("All frames failed. Try dimensions=720, check network, "
                         "or use export_to_drive() instead.")

    fps = max(1.0, len(imgs) / target_seconds)     # fit the clip to ~target_seconds
    imageio.mimsave(out_path, imgs, fps=fps, codec="libx264", quality=8)
    print(f"Wrote {out_path}  ({len(imgs)} frames @ {fps:.2f} fps = {len(imgs)/fps:.0f}s)")
    pub = os.path.join(os.path.dirname(os.path.abspath(__file__)), "remotion-sawah", "public")
    if os.path.isdir(pub):                          # auto-copy into the Remotion project
        shutil.copy(out_path, os.path.join(pub, "urban_sprawl.mp4"))
        print("Copied to", os.path.join(pub, "urban_sprawl.mp4"))

if __name__ == "__main__":
    # Pick one:
    # export_to_drive()      # MP4 lands in your Drive 'earthengine' folder
    render_local()           # fits the clip to ~17s (Act 1)

# NOTES
# - Blank early frames = no Landsat coverage that year -> raise START_YEAR.
# - Stripes 2003-2013 = Landsat-7 SLC-off; median hides most. Prefer L5/L8 years.
# - Stronger sawah->urban contrast: switch to the false-color VIS above.
# - getThumbURL caps ~ a few MP; 1080 px is fine. For 4K, use export_to_drive().
