#!/usr/bin/env python3
"""
PADDY CLASSIFICATION over Java  ·  Sentinel-1 + Sentinel-2  ·  Random Forest
Training data: Research/training_points_random_java.csv
  columns (sep=';'): tanggal | lintang(lat) | bujur(lon) | paddy(0/1)
  all points dated 2024-05-15 -> classify the 2024 main season.

Relates to [[PUPR]] / rice-growth-stage-mapping and [[Traffic Analyses]] vault notes.

Install:
    pip install earthengine-api pandas
"""

import os
import ee
import pandas as pd

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

# --- 1. TRAINING POINTS (local CSV -> FeatureCollection) ---------------
CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "training_points_random_java.csv")
df = pd.read_csv(CSV, sep=";")
print(f"Loaded {len(df)} points  |  paddy=1: {int(df.paddy.sum())}, "
      f"paddy=0: {int((df.paddy == 0).sum())}")

points = ee.FeatureCollection([
    ee.Feature(ee.Geometry.Point([float(r.bujur), float(r.lintang)]),
               {"paddy": int(r.paddy)})
    for r in df.itertuples()
])

# --- 2. AREA + SEASON --------------------------------------------------
JAVA = ee.Geometry.Rectangle([105.0, -8.9, 114.7, -5.8])   # rough Java bbox
START, END = "2024-01-01", "2024-06-30"                     # 2024 main season

# --- 3. SENTINEL-2 SEASONAL FEATURES (optical) ------------------------
def mask_s2(img):
    scl = img.select("SCL")
    bad = (scl.eq(3)                      # shadow
           .Or(scl.eq(8)).Or(scl.eq(9))  # cloud med/high
           .Or(scl.eq(10)).Or(scl.eq(11)))  # cirrus / snow
    return img.updateMask(bad.Not())

s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
      .filterBounds(JAVA).filterDate(START, END)
      .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
      .map(mask_s2))

def add_indices(img):
    img = img.divide(10000)              # reflectance
    ndvi = img.normalizedDifference(["B8", "B4"]).rename("NDVI")
    ndwi = img.normalizedDifference(["B3", "B8"]).rename("NDWI")     # water
    mndwi = img.normalizedDifference(["B3", "B11"]).rename("MNDWI")
    lswi = img.normalizedDifference(["B8", "B11"]).rename("LSWI")    # flooding (paddy!)
    evi = img.expression(
        "2.5*((N-R)/(N+6*R-7.5*B+1))",
        {"N": img.select("B8"), "R": img.select("B4"), "B": img.select("B2")}
    ).rename("EVI")
    return img.addBands([ndvi, ndwi, mndwi, lswi, evi])

s2 = s2.map(add_indices)

# seasonal median reflectance + index percentiles/amplitude
s2_med = s2.select(["B2", "B3", "B4", "B8", "B11", "B12"]).median()
ndvi_stats = s2.select("NDVI").reduce(
    ee.Reducer.percentile([10, 50, 90]).combine(ee.Reducer.stdDev(), sharedInputs=True))
lswi_med = s2.select("LSWI").median().rename("LSWI_med")
mndwi_max = s2.select("MNDWI").max().rename("MNDWI_max")     # peak flooding signal
evi_med = s2.select("EVI").median().rename("EVI_med")

# --- 4. SENTINEL-1 SEASONAL FEATURES (SAR, cloud-free) ----------------
s1 = (ee.ImageCollection("COPERNICUS/S1_GRD")
      .filterBounds(JAVA).filterDate(START, END)
      .filter(ee.Filter.eq("instrumentMode", "IW"))
      .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
      .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
      .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
      .select(["VV", "VH"]))

s1_stats = s1.reduce(
    ee.Reducer.mean().combine(ee.Reducer.minMax(), sharedInputs=True)
    .combine(ee.Reducer.stdDev(), sharedInputs=True))     # VV/VH mean,min,max,stdDev
# VH minimum captures the transplanting/flooding dip that marks paddy.

# --- 5. FEATURE STACK -------------------------------------------------
stack = (s2_med
         .addBands(ndvi_stats).addBands(lswi_med).addBands(mndwi_max).addBands(evi_med)
         .addBands(s1_stats)
         .clip(JAVA))
BANDS = stack.bandNames()

# --- 6. SAMPLE + SPLIT -------------------------------------------------
samples = stack.sampleRegions(
    collection=points, properties=["paddy"], scale=10, tileScale=4, geometries=False)
samples = samples.randomColumn("rnd", seed=42)
train = samples.filter(ee.Filter.lt("rnd", 0.7))
test = samples.filter(ee.Filter.gte("rnd", 0.7))

# --- 7. TRAIN RANDOM FOREST -------------------------------------------
clf = ee.Classifier.smileRandomForest(150).train(
    features=train, classProperty="paddy", inputProperties=BANDS)

# --- 8. ACCURACY (holdout) --------------------------------------------
cm = test.classify(clf).errorMatrix("paddy", "classification")
print("Confusion matrix:", cm.getInfo())
print("Overall accuracy:", cm.accuracy().getInfo())
print("Kappa:", cm.kappa().getInfo())

# Feature importance (which bands carry the signal)
imp = clf.explain().get("importance").getInfo()
print("Top features:", sorted(imp.items(), key=lambda kv: -kv[1])[:10])

# --- 9. CLASSIFY + EXPORT ---------------------------------------------
paddy_map = stack.classify(clf).rename("paddy").byte()

def export_map():
    task = ee.batch.Export.image.toDrive(
        image=paddy_map,
        description="paddy_java_2024",
        folder="earthengine",
        region=JAVA,
        scale=10,
        maxPixels=int(1e13),
        crs="EPSG:4326",
    )
    task.start()
    print("Export started:", task.id, task.status()["state"])

if __name__ == "__main__":
    # Accuracy prints above on run. Uncomment to export the wall-to-wall map:
    # export_map()
    pass

# NOTES
# - LSWI/MNDWI + S1 VH-min are the paddy-specific features (flooding + transplant dip).
# - Single-date labels (2024-05-15) -> seasonal window Jan-Jun 2024. Adjust START/END
#   per planting calendar of your AOI.
# - For rice GROWTH STAGE (not just presence), swap the binary RF for a per-pixel
#   S1 VH / S2 NDVI time-series + phenology metrics -> ties to rice-growth-stage-mapping.
# - Export over all Java is heavy; test on a province first (swap JAVA for a GAUL geom:
#   ee.FeatureCollection('FAO/GAUL/2015/level1').filter(ee.Filter.eq('ADM1_NAME','Jawa Tengah'))).
