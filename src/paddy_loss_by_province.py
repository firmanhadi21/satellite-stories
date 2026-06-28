#!/usr/bin/env python3
"""
SAWAH LOSS BY PROVINCE IN JAVA  ·  30 m  ·  1985-2022
Per-province trend of irrigated cropland (~ sawah) from GLC-FCS30D.
Ranks the 6 Java provinces by how much paddy they lost.

Companion to paddy_decadal_trend_glcfcs30d.py (Java-wide). Validate against
BPS "Lahan Baku Sawah" per-province statistics.

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

# --- 1. JAVA PROVINCES -----------------------------------------------
PROVINCES = ["Jawa Barat", "Jawa Tengah", "Jawa Timur", "Banten",
             "Daerah Istimewa Yogyakarta", "Jakarta Raya"]
JAVA = (ee.FeatureCollection("FAO/GAUL/2015/level1")
        .filter(ee.Filter.inList("ADM1_NAME", PROVINCES)))

# --- 2. GLC-FCS30D + year->band map ----------------------------------
annual_ic = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/annual")
fiveyr_ic = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/five-years-map")
annual = annual_ic.mosaic()
fiveyr = fiveyr_ic.mosaic()
print("annual bands:", ee.Image(annual_ic.first()).bandNames().getInfo())   # expect b1..b23

series = [(1985, fiveyr, "b1"), (1990, fiveyr, "b2"), (1995, fiveyr, "b3")]
for i, y in enumerate(range(2000, 2023)):
    series.append((y, annual, f"b{i + 1}"))

PADDY_CLASS = 20      # irrigated cropland ~ sawah
SCALE = 100           # coarsen 30 m for tractable per-province area sums

# --- 3. PER-YEAR, ALL PROVINCES AT ONCE (reduceRegions) --------------
recs = []
for year, img, band in series:
    paddy_area = (img.select(band).remap([10, 20], [1, 1], 0)   # sawah proxy = rainfed+irrigated (class 20 alone fails in Java)
                  .multiply(ee.Image.pixelArea()).rename("area"))
    fc = paddy_area.reduceRegions(
        collection=JAVA, reducer=ee.Reducer.sum(), scale=SCALE, tileScale=8)
    for f in fc.getInfo()["features"]:
        p = f["properties"]
        val = p.get("sum", p.get("area", 0)) or 0   # reduceRegions key = reducer or band name
        recs.append({"province": p["ADM1_NAME"], "year": year,
                     "paddy_km2": val / 1e6})
    print(f"{year} done")

df = pd.DataFrame(recs)
wide = df.pivot(index="year", columns="province", values="paddy_km2").sort_index()

# --- 4. PER-PROVINCE TREND + RANK ------------------------------------
summary = []
for prov in wide.columns:
    s = wide[prov].dropna()
    slope = np.polyfit(s.index, s.values, 1)[0]          # km^2/yr
    first, last = s.iloc[0], s.iloc[-1]
    pct = (last - first) / first * 100 if first else np.nan
    summary.append({"province": prov,
                    "start_km2": round(first, 1),
                    "end_km2": round(last, 1),
                    "net_km2": round(last - first, 1),
                    "pct_change": round(pct, 1),
                    "slope_ha_per_yr": round(slope * 100, 0)})

rank = pd.DataFrame(summary).sort_values("net_km2")        # most loss first
print("\n=== SAWAH (irrigated cropland) CHANGE BY PROVINCE, 1985->2022 ===")
print(rank.to_string(index=False))

# --- 5. SAVE CSV + CHART ---------------------------------------------
here = os.path.dirname(os.path.abspath(__file__))
wide.to_csv(os.path.join(here, "java_paddy_by_province_timeseries.csv"))
rank.to_csv(os.path.join(here, "java_paddy_loss_ranking.csv"), index=False)
print("Saved CSVs to Research/")

try:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(9, 5))
    for prov in wide.columns:
        plt.plot(wide.index, wide[prov], "o-", ms=3, label=prov)
    plt.title("Sawah (irrigated cropland) by Java province, 1985–2022 (GLC-FCS30D)")
    plt.xlabel("Year"); plt.ylabel("Area (km²)")
    plt.legend(fontsize=8); plt.tight_layout()
    out = os.path.join(here, "java_paddy_by_province.png")
    plt.savefig(out, dpi=150)
    print("Saved chart:", out)
except ImportError:
    print("(install matplotlib for the chart)")

# NOTES
# - Negative net_km2 / pct_change = sawah loss; the table is sorted most-loss-first.
# - "Irrigated cropland" ~ sawah proxy; validate ranking vs BPS Lahan Baku Sawah per province.
# - SCALE=100 for tractability; drop to 30 for precision (slower) or Export per province.
# - For the story: the top-loss province is your case study; pair with the
#   urban-sprawl time-lapse centered there (social-media/gee_urban_sprawl_timelapse.py).
