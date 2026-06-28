#!/usr/bin/env python3
"""
Export method-explainer STILLS for the Bekasi-Karawang AOI (Sentinel-2, 2024):
  ndbi.png       - built-up index (built-up bright orange/red)
  ndvi.png       - vegetation index (vegetation bright green)
  falsecolor.png - NIR-R-G (vegetation red)
Saves to social-media/ and copies into remotion-sawah/public/.

Install:  pip install earthengine-api requests pillow
"""

import os
import io
import time
import shutil
import ee
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
CRED_DIR = os.path.join(HERE, "..", "Credentials")
PUBLIC = os.path.join(HERE, "remotion-sawah", "public")

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

# Same AOI as the time-lapse (Bekasi-Karawang corridor)
center = ee.Geometry.Point([107.22, -6.31])
aoi = center.buffer(9000).bounds()

def mask_s2(img):
    scl = img.select("SCL")
    bad = scl.eq(3).Or(scl.eq(8)).Or(scl.eq(9)).Or(scl.eq(10)).Or(scl.eq(11))
    return img.updateMask(bad.Not())

s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
      .filterBounds(aoi).filterDate("2024-01-01", "2024-12-31")
      .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40))
      .map(mask_s2).median().divide(10000))

ndvi = s2.normalizedDifference(["B8", "B4"])              # vegetation
ndbi = s2.normalizedDifference(["B11", "B8"])             # built-up

# Sentinel-1 (radar): built-up = strong & STABLE VV; sawah = high VH variability (seasonal)
s1 = (ee.ImageCollection("COPERNICUS/S1_GRD").filterBounds(aoi)
      .filterDate("2024-01-01", "2024-12-31")
      .filter(ee.Filter.eq("instrumentMode", "IW"))
      .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING")))
vv_mean = s1.select("VV").mean()                          # built-up bright & steady
vh_std = s1.select("VH").reduce(ee.Reducer.stdDev())      # sawah flickers across seasons

LAYERS = {
    "s1_builtup.png": vv_mean.visualize(min=-18, max=-2,
                          palette=["08081f", "1f3b73", "3a7ca5", "ffd24a", "ff7043", "d7191c"]),
    "s1_sawah.png": vh_std.visualize(min=0.5, max=4.0,
                          palette=["08081f", "1f3b73", "3a7ca5", "9bc24a", "ffff66", "ffffff"]),
    "ndvi.png": ndvi.visualize(min=0.0, max=0.8,
                               palette=["ffffff", "d9f0a3", "78c679", "238443", "004529"]),
    "ndbi.png": ndbi.visualize(min=-0.2, max=0.4,
                               palette=["ffffff", "fee391", "fe9929", "d95f0e", "993404"]),
    "falsecolor.png": s2.visualize(bands=["B8", "B4", "B3"], min=0.0, max=0.35, gamma=1.1),
}

def save(img, name, attempts=5):
    for a in range(attempts):
        try:
            url = img.clip(aoi).getThumbURL(
                {"region": aoi, "dimensions": 1200, "format": "png", "crs": "EPSG:3857"})
            r = requests.get(url, timeout=180)
            r.raise_for_status()
            out = os.path.join(HERE, name)
            with open(out, "wb") as f:
                f.write(r.content)
            os.makedirs(PUBLIC, exist_ok=True)
            shutil.copy(out, os.path.join(PUBLIC, name))
            print("Wrote", name, "(+ public/)")
            return
        except Exception as e:
            print("  retry", name, e)
            time.sleep(3 * (a + 1))
    print("  FAILED", name)

if __name__ == "__main__":
    for name, img in LAYERS.items():
        save(img, name)
