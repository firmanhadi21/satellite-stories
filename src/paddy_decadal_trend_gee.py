#!/usr/bin/env python3
"""
IS CROPLAND / PADDY DECREASING IN JAVA OVER DECADES?
Annual cropland-area trend over Java from MODIS MCD12Q1 (2001-2023).

This answers the DECADAL question (your 2024 RF classifier in
paddy_classification_gee.py cannot — Sentinel only goes back ~2015).
NOTE: MODIS gives "cropland", a PROXY for sawah, at 500 m. Cross-check the
trend against BPS "Lahan Baku Sawah" official statistics, and see the
30 m GLC-FCS30D option (irrigated-cropland class = paddy proxy) at the bottom.

Install:
    pip install earthengine-api pandas numpy matplotlib
"""

import os
import ee
import pandas as pd
import numpy as np

# --- 0. CONNECT (reads ../Credentials/gee.txt + service-account key) ---
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
KEY_FILE = os.path.join(CRED_DIR, "ee-geodetic.json")
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser(cfg.get("GEE_SERVICE_ACCOUNT_KEY_FILE", ""))
ee.Initialize(ee.ServiceAccountCredentials(SA_EMAIL, KEY_FILE), project=PROJECT)
print(f"Connected to GEE project: {PROJECT}")

# --- 1. JAVA AOI (province polygons, land only) -----------------------
gaul = ee.FeatureCollection("FAO/GAUL/2015/level1")
JAVA = gaul.filter(ee.Filter.inList("ADM1_NAME", [
    "Jawa Barat", "Jawa Tengah", "Jawa Timur", "Banten",
    "Daerah Istimewa Yogyakarta", "Jakarta Raya"]))
JAVA_GEOM = JAVA.geometry()

# --- 2. CROPLAND AREA PER YEAR (MODIS MCD12Q1, IGBP) ------------------
# LC_Type1: 12 = Croplands, 14 = Cropland/Natural-vegetation mosaic
mcd = ee.ImageCollection("MODIS/061/MCD12Q1")
YEARS = list(range(2001, 2024))

def cropland_km2(year):
    img = mcd.filterDate(f"{year}-01-01", f"{year}-12-31").first().select("LC_Type1")
    crop = img.eq(12).Or(img.eq(14))                       # cropland mask
    area = crop.multiply(ee.Image.pixelArea()).rename("area")   # m^2 where cropland
    total = area.reduceRegion(
        reducer=ee.Reducer.sum(), geometry=JAVA_GEOM, scale=500,
        maxPixels=int(1e13), tileScale=4).get("area")
    return (total.getInfo() or 0) / 1e6

# Sequential per-year requests -> avoids "Too many concurrent aggregations".
recs = []
for y in YEARS:
    km2 = cropland_km2(y)
    recs.append({"year": y, "cropland_km2": km2})
    print(f"{y}: {km2:,.0f} km^2")
df = pd.DataFrame(recs).sort_values("year").reset_index(drop=True)

# --- 3. TREND ---------------------------------------------------------
slope, intercept = np.polyfit(df["year"], df["cropland_km2"], 1)   # km^2 / year
first3 = df["cropland_km2"].head(3).mean()
last3 = df["cropland_km2"].tail(3).mean()
pct = (last3 - first3) / first3 * 100
print(f"\nTrend slope : {slope:,.0f} km^2/year  ({slope*100:,.0f} ha/year)")
print(f"2001-03 mean: {first3:,.0f} km^2   2021-23 mean: {last3:,.0f} km^2")
print(f"Net change  : {pct:+.1f}% over the period")
print("DECREASING" if slope < 0 else "increasing/stable")

# --- 4. CHART ---------------------------------------------------------
try:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 4.5))
    plt.plot(df["year"], df["cropland_km2"], "o-", label="MODIS cropland")
    plt.plot(df["year"], intercept + slope * df["year"], "--",
             label=f"trend {slope:,.0f} km²/yr")
    plt.title("Java cropland area, 2001–2023 (MODIS MCD12Q1)")
    plt.xlabel("Year"); plt.ylabel("Cropland area (km²)")
    plt.legend(); plt.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "java_cropland_trend.png")
    plt.savefig(out, dpi=150)
    print("Saved chart:", out)
except ImportError:
    print("(install matplotlib for the chart)")

# NOTES / next steps
# - Cross-check with BPS "Luas Lahan Baku Sawah (LBS)" / BPS sawah harvested-area
#   statistics — those are the authoritative sawah numbers for Java.
# - 30 m, 1985-2022, paddy-specific proxy via GLC-FCS30D (community asset):
#     col = ee.ImageCollection('projects/sat-io/open-datasets/GLC-FCS30D/annual')
#     # band per year 2000-2022; class 20 = Irrigated cropland (~ sawah), 10 = Rainfed.
#     # Verify the asset id + class codes in the awesome-gee-community-catalog before use.
# - WHERE the loss goes: pair this with the urban-sprawl Landsat time-lapse
#   (social-media/gee_urban_sprawl_timelapse.py) — sawah -> built-up is the main driver.
