#!/usr/bin/env python3
"""
KONAWE NICKEL-MINING DESTRUCTION TIME-LAPSE (Landsat NDVI loss).
Forest = GREEN (high NDVI), cleared mine/bare = BROWN-RED (low NDVI). Monotonic:
once forest is stripped for nickel it stays bare. Also prints forest-loss hectares
(Hansen Global Forest Change) inside the AOI for Act 3.

Writes konawe_timelapse.mp4 and auto-copies to remotion-sawah/public/.

Install:  pip install earthengine-api requests pillow imageio imageio-ffmpeg numpy
"""

import os
import ee

# --- 0. CONNECT (reads ../Credentials/gee.txt + service-account key) ---
CRED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Credentials")

def _cfg(path):
    c = {}
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            c[k.strip()] = v.strip()
    return c

cfg = _cfg(os.path.join(CRED_DIR, "gee.txt"))
KEY = os.path.join(CRED_DIR, "ee-geodetic.json")
if not os.path.exists(KEY):
    KEY = os.path.expanduser(cfg.get("GEE_SERVICE_ACCOUNT_KEY_FILE", ""))
ee.Initialize(ee.ServiceAccountCredentials(cfg["GEE_SERVICE_ACCOUNT_EMAIL"], KEY),
              project=cfg.get("GEE_PROJECT_ID", "ee-geodeticengineeringundip"))
print("Connected.")

# --- 1. AREA — Konawe Utara nickel belt (Lasolo/Molawe/Andowia) --------
center = ee.Geometry.Point([122.174, -3.528])   # Konawe nickel mine (shifted 2km E)
aoi = center.buffer(6000).bounds()              # ~12 km box (matches konawe_aoi.geojson)

YEARS = [2000, 2010, 2014, 2016, 2018, 2020, 2022, 2024]   # pre-boom -> mining expansion

# --- 2. LANDSAT C2 L2: cloud mask + scale + NDVI ----------------------
def mask_l2(img):
    qa = img.select("QA_PIXEL")
    m = (qa.bitwiseAnd(1 << 1).eq(0).And(qa.bitwiseAnd(1 << 3).eq(0))
         .And(qa.bitwiseAnd(1 << 4).eq(0)).And(qa.bitwiseAnd(1 << 2).eq(0)))
    return img.updateMask(m)

def prep(img, era):
    img = mask_l2(img)
    b = (img.select(["SR_B3", "SR_B4"], ["red", "nir"]) if era == "old"
         else img.select(["SR_B4", "SR_B5"], ["red", "nir"]))
    return b.multiply(0.0000275).add(-0.2).copyProperties(img, ["system:time_start"])

L5 = ee.ImageCollection("LANDSAT/LT05/C02/T1_L2").map(lambda i: prep(i, "old"))
L7 = ee.ImageCollection("LANDSAT/LE07/C02/T1_L2").map(lambda i: prep(i, "old"))
L8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2").map(lambda i: prep(i, "new"))
L9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2").map(lambda i: prep(i, "new"))
landsat = L5.merge(L7).merge(L8).merge(L9).filterBounds(aoi)

# NDVI palette: low = brown/red (bare mine), high = green (forest)
NDVI_VIS = {"min": 0.1, "max": 0.8,
            "palette": ["a50026", "d73027", "f46d43", "fdae61", "fee08b",
                        "d9ef8b", "a6d96a", "1a9850", "006837"]}

def annual_rgb(year):
    annual = landsat.filterDate(f"{year}-01-01", f"{year}-12-31").median()
    ndvi = annual.normalizedDifference(["nir", "red"]).rename("NDVI")
    return ndvi.visualize(**NDVI_VIS).clip(aoi).set("year", year)

# --- 3. FOREST-LOSS HECTARES in the AOI (Hansen GFC) for Act 3 --------
def forest_loss_ha():
    gfc = ee.Image("UMD/hansen/global_forest_change_2025_v1_13")
    loss = gfc.select("loss")                      # tree-cover loss 2001-2024
    area = loss.multiply(ee.Image.pixelArea()).reduceRegion(
        reducer=ee.Reducer.sum(), geometry=aoi, scale=30, maxPixels=int(1e13))
    return ee.Number(area.get("loss")).divide(1e4).getInfo()   # m^2 -> ha

# --- 4. QUICK PREVIEW -------------------------------------------------
frames = ee.ImageCollection([annual_rgb(y) for y in YEARS])
print("Animation preview:")
print(frames.getVideoThumbURL({"dimensions": 600, "framesPerSecond": 1,
                               "region": aoi, "crs": "EPSG:3857"}))

# --- 5. LOCAL RENDER (year label + fit ~17s + auto-copy) -------------
def render_local(out_path=None, dimensions=1080, target_seconds=17):
    if out_path is None:
        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "konawe_timelapse.mp4")
    import io, time, shutil, requests
    import numpy as np
    import imageio.v2 as imageio
    from PIL import Image, ImageDraw, ImageFont

    fsize = dimensions // 8
    font = None
    for p in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/System/Library/Fonts/Helvetica.ttc", "DejaVuSans-Bold.ttf"]:
        try:
            font = ImageFont.truetype(p, fsize); break
        except OSError:
            continue
    if font is None:
        try:
            font = ImageFont.load_default(size=fsize)
        except TypeError:
            font = ImageFont.load_default()

    def fetch(y, attempts=5):
        last = None
        for a in range(attempts):
            try:
                url = annual_rgb(y).getThumbURL(
                    {"region": aoi, "dimensions": dimensions, "format": "png", "crs": "EPSG:3857"})
                r = requests.get(url, timeout=180); r.raise_for_status()
                im = Image.open(io.BytesIO(r.content)).convert("RGB")
                d = ImageDraw.Draw(im)
                lbl, m, pad = str(y), dimensions // 30, dimensions // 70
                bb = d.textbbox((0, 0), lbl, font=font, stroke_width=5)
                tw, th = bb[2] - bb[0], bb[3] - bb[1]
                d.rectangle([m - pad, m - pad, m + tw + pad, m + th + pad * 2], fill=(0, 0, 0))
                d.text((m - bb[0], m - bb[1]), lbl, font=font, fill="white",
                       stroke_width=5, stroke_fill="black")
                print("  frame", y, "ok")
                return np.array(im)
            except Exception as e:
                last = e; time.sleep(3 * (a + 1))
        print(f"  year {y} FAILED: {last}"); return None

    imgs = [a for a in (fetch(y) for y in YEARS) if a is not None]
    if not imgs:
        raise SystemExit("All frames failed; try dimensions=720 or check network.")
    fps = max(1.0, len(imgs) / target_seconds)
    imageio.mimsave(out_path, imgs, fps=fps, codec="libx264", quality=8)
    print(f"Wrote {out_path}  ({len(imgs)} frames @ {fps:.2f} fps = {len(imgs)/fps:.0f}s)")
    pub = os.path.join(os.path.dirname(os.path.abspath(__file__)), "remotion-konawe", "public")
    if os.path.isdir(pub):
        shutil.copy(out_path, os.path.join(pub, "konawe_timelapse.mp4"))
        print("Copied to", os.path.join(pub, "konawe_timelapse.mp4"))

if __name__ == "__main__":
    print(f"Forest loss in AOI (Hansen 2001-2024): {forest_loss_ha():,.0f} ha")
    render_local()
