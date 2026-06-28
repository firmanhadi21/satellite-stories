#!/usr/bin/env python3
"""
PADDY (IRRIGATED CROPLAND) DECADAL TREND IN JAVA  ·  30 m  ·  1985-2022
Source: GLC-FCS30D (Zhang et al., 2024, ESSD) via the awesome-gee-community
catalog (sat-io). 30 m global land cover, paddy-specific via the
"Irrigated cropland" class (~ sawah in tropical Java).

This is the high-res, paddy-specific companion to paddy_decadal_trend_gee.py
(MODIS cropland proxy). Validate both against BPS "Lahan Baku Sawah" stats.

VERIFY before trusting: GLC-FCS30D is a community asset. The script prints the
band names so you can confirm structure (annual: b1=2000 ... b23=2022;
five-years: b1=1985, b2=1990, b3=1995). Class codes (GLC_FCS30 fine system):
  10 Rainfed cropland | 11 Herbaceous-cover crop | 12 Tree/shrub (orchard)
  20 Irrigated cropland  <-- paddy proxy

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

# --- 1. JAVA AOI ------------------------------------------------------
gaul = ee.FeatureCollection("FAO/GAUL/2015/level1")
JAVA = gaul.filter(ee.Filter.inList("ADM1_NAME", [
    "Jawa Barat", "Jawa Tengah", "Jawa Timur", "Banten",
    "Daerah Istimewa Yogyakarta", "Jakarta Raya"]))
JAVA_GEOM = JAVA.geometry()

# --- 2. GLC-FCS30D ASSETS --------------------------------------------
ANNUAL_ID = "projects/sat-io/open-datasets/GLC-FCS30D/annual"
FIVEYR_ID = "projects/sat-io/open-datasets/GLC-FCS30D/five-years-map"

annual_ic = ee.ImageCollection(ANNUAL_ID)
fiveyr_ic = ee.ImageCollection(FIVEYR_ID)
annual = annual_ic.mosaic()        # bands b1..b23 -> 2000..2022
fiveyr = fiveyr_ic.mosaic()        # bands b1..b3  -> 1985,1990,1995

# SELF-CHECK: confirm asset structure before trusting results
print("annual band names:", ee.Image(annual_ic.first()).bandNames().getInfo())
print("five-yr band names:", ee.Image(fiveyr_ic.first()).bandNames().getInfo())

# --- 3. YEAR -> (image, band) MAP ------------------------------------
series = [(1985, fiveyr, "b1"), (1990, fiveyr, "b2"), (1995, fiveyr, "b3")]
for i, y in enumerate(range(2000, 2023)):          # 2000..2022 -> b1..b23
    series.append((y, annual, f"b{i + 1}"))

PADDY_CLASS = 20                                    # irrigated cropland
CROPLAND_CLASSES = [10, 11, 12, 20]                # all cropland (context)
SCALE = 100        # area-reduction scale (coarsen 30 m for tractability over all Java)

def area_km2(mask):
    res = mask.multiply(ee.Image.pixelArea()).rename("area").reduceRegion(
        reducer=ee.Reducer.sum(), geometry=JAVA_GEOM,
        scale=SCALE, maxPixels=int(1e13), tileScale=8)
    return ee.Number(res.get("area")).divide(1e6)

# --- 4. AREA PER TIME STEP (per-year requests; robust vs timeouts) ---
recs = []
for year, img, band in series:
    cls = img.select(band)
    paddy = area_km2(cls.remap([10, 20], [1, 1], 0)).getInfo()  # sawah proxy = rainfed+irrigated annual cropland (class 20 alone fails in Java)
    crop = area_km2(cls.remap(CROPLAND_CLASSES, [1] * len(CROPLAND_CLASSES), 0)).getInfo()
    recs.append({"year": year, "paddy_km2": paddy, "cropland_km2": crop})
    print(f"{year}: paddy={paddy:,.0f} km^2  cropland={crop:,.0f} km^2")

df = pd.DataFrame(recs).sort_values("year").reset_index(drop=True)

# --- 5. TREND (paddy / irrigated cropland) ---------------------------
slope, intercept = np.polyfit(df["year"], df["paddy_km2"], 1)   # km^2/yr
first = df["paddy_km2"].iloc[0]
last = df["paddy_km2"].iloc[-1]
pct = (last - first) / first * 100
print(f"\nPaddy (irrigated cropland) trend: {slope:,.0f} km^2/yr ({slope*100:,.0f} ha/yr)")
print(f"{df.year.iloc[0]}: {first:,.0f} km^2  ->  {df.year.iloc[-1]}: {last:,.0f} km^2  "
      f"({pct:+.1f}%)")
print("DECREASING" if slope < 0 else "increasing/stable")

# --- 6. CHART ---------------------------------------------------------
try:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8.5, 4.5))
    plt.plot(df["year"], df["paddy_km2"], "o-", color="tab:green",
             label="Irrigated cropland (~paddy)")
    plt.plot(df["year"], df["cropland_km2"], "s--", color="tab:olive",
             alpha=.6, label="All cropland")
    plt.plot(df["year"], intercept + slope * df["year"], ":", color="tab:red",
             label=f"paddy trend {slope:,.0f} km²/yr")
    plt.title("Java paddy/cropland area, 1985–2022 (GLC-FCS30D, 30 m)")
    plt.xlabel("Year"); plt.ylabel("Area (km²)")
    plt.legend(); plt.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "java_paddy_trend_glcfcs30d.png")
    plt.savefig(out, dpi=150)
    print("Saved chart:", out)
except ImportError:
    print("(install matplotlib for the chart)")

# NOTES
# - If band names above are NOT b1..b23 / b1..b3, fix the year->band map (Section 3)
#   from the printed names. Check the awesome-gee-community-catalog GLC_FCS30D page.
# - "Irrigated cropland" ~ sawah in Java but may include other irrigated crops; treat
#   as a strong PROXY, validate against BPS Lahan Baku Sawah.
# - SCALE=100 coarsens 30 m for whole-Java area sums (keeps reduceRegion tractable).
#   For 30 m precision, loop per province (filter GAUL ADM1_NAME) or Export.image.
# - WHERE loss goes: pair with social-media/gee_urban_sprawl_timelapse.py (sawah->built-up).
