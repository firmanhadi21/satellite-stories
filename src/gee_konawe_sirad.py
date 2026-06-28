#!/usr/bin/env python3
"""
SIRAD over Konawe — Sentinel-1 multitemporal radar deforestation map.
SIRAD = Sistema de Indicação Radar de Desmatamento (Juan Doblas, Instituto
Socioambiental). Refined Lee speckle filter by Guido Lemoine. Python port.

Method: mean VH backscatter for 3 periods -> RGB composite.
  - Stable land (forest stays forest, mine stays mine) -> GREY
  - Cleared between periods -> COLOURED (the hue encodes WHEN it was cleared)
Outputs sirad_konawe.png (RGB composite) + sirad_diff_konawe.png (p2->p3 change),
auto-copied to remotion-sawah/public/.

Install:  pip install earthengine-api requests pillow
"""

import os
import io
import time
import shutil
import ee
import requests
from PIL import Image

# --- connect ----------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
CRED = os.path.join(HERE, "..", "Credentials")
def _cfg(p):
    c = {}
    for ln in open(p):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1); c[k.strip()] = v.strip()
    return c
cfg = _cfg(os.path.join(CRED, "gee.txt"))
KEY = os.path.join(CRED, "ee-geodetic.json")
if not os.path.exists(KEY):
    KEY = os.path.expanduser(cfg.get("GEE_SERVICE_ACCOUNT_KEY_FILE", ""))
ee.Initialize(ee.ServiceAccountCredentials(cfg["GEE_SERVICE_ACCOUNT_EMAIL"], KEY),
              project=cfg.get("GEE_PROJECT_ID", "ee-geodeticengineeringundip"))
print("Connected.")

# --- AOI + SIRAD periods (4 dates -> 3 periods) -----------------------
center = ee.Geometry.Point([122.174, -3.528])    # Konawe nickel mine (shifted 2km E)
aoi = center.buffer(6000).bounds()               # ~12 km box (matches konawe_aoi.geojson)
# 4 dates (T1..T4) -> 3 periods. The RGB composite maps:
#   RED   = period 1 mean VH  (T1 -> T2)
#   GREEN = period 2 mean VH  (T2 -> T3)
#   BLUE  = period 3 mean VH  (T3 -> T4)
DATES = ["2017-04-01", "2018-04-01", "2020-04-01", "2026-04-01"]
POL = "VH"
USE_LEE = False    # Refined Lee exceeds the thumbnail memory limit; use focal-median despeckle.
                   # Set True only if you export via Drive (Export.image), not getThumbURL.

# --- dB helpers -------------------------------------------------------
def toNatural(img):
    return ee.Image(10.0).pow(img.select(0).divide(10.0))
def toDB(img):
    return ee.Image(img).log10().multiply(10.0)

def maskEdge(img):
    m = (img.select(0).unitScale(-25, 5).multiply(255).toByte()
         .connectedComponents(ee.Kernel.rectangle(1, 1), 100))
    return img.updateMask(m.select(0))

# --- Refined Lee speckle filter (Guido Lemoine; natural units) --------
def RefinedLee(img):
    w3 = ee.List.repeat(ee.List.repeat(1, 3), 3)
    k3 = ee.Kernel.fixed(3, 3, w3, 1, 1, False)
    mean3 = img.reduceNeighborhood(ee.Reducer.mean(), k3)
    var3 = img.reduceNeighborhood(ee.Reducer.variance(), k3)
    sw = ee.List([[0,0,0,0,0,0,0],[0,1,0,1,0,1,0],[0,0,0,0,0,0,0],
                  [0,1,0,1,0,1,0],[0,0,0,0,0,0,0],[0,1,0,1,0,1,0],[0,0,0,0,0,0,0]])
    sk = ee.Kernel.fixed(7, 7, sw, 3, 3, False)
    sample_mean = mean3.neighborhoodToBands(sk)
    sample_var = var3.neighborhoodToBands(sk)
    grad = sample_mean.select(1).subtract(sample_mean.select(7)).abs()
    grad = grad.addBands(sample_mean.select(6).subtract(sample_mean.select(2)).abs())
    grad = grad.addBands(sample_mean.select(3).subtract(sample_mean.select(5)).abs())
    grad = grad.addBands(sample_mean.select(0).subtract(sample_mean.select(8)).abs())
    max_grad = grad.reduce(ee.Reducer.max())
    gradmask = grad.eq(max_grad)
    gradmask = gradmask.addBands(gradmask)
    d = sample_mean.select(1).subtract(sample_mean.select(4)).gt(
        sample_mean.select(4).subtract(sample_mean.select(7))).multiply(1)
    d = d.addBands(sample_mean.select(6).subtract(sample_mean.select(4)).gt(
        sample_mean.select(4).subtract(sample_mean.select(2))).multiply(2))
    d = d.addBands(sample_mean.select(3).subtract(sample_mean.select(4)).gt(
        sample_mean.select(4).subtract(sample_mean.select(5))).multiply(3))
    d = d.addBands(sample_mean.select(0).subtract(sample_mean.select(4)).gt(
        sample_mean.select(4).subtract(sample_mean.select(8))).multiply(4))
    d = d.addBands(d.select(0).Not().multiply(5))
    d = d.addBands(d.select(1).Not().multiply(6))
    d = d.addBands(d.select(2).Not().multiply(7))
    d = d.addBands(d.select(3).Not().multiply(8))
    d = d.updateMask(gradmask).reduce(ee.Reducer.sum())
    stats = sample_var.divide(sample_mean.multiply(sample_mean))
    sigmaV = stats.toArray().arraySort().arraySlice(0, 0, 5).arrayReduce(ee.Reducer.mean(), [0])
    rect_w = ee.List.repeat(ee.List.repeat(0, 7), 3).cat(ee.List.repeat(ee.List.repeat(1, 7), 4))
    diag_w = ee.List([[1,0,0,0,0,0,0],[1,1,0,0,0,0,0],[1,1,1,0,0,0,0],[1,1,1,1,0,0,0],
                      [1,1,1,1,1,0,0],[1,1,1,1,1,1,0],[1,1,1,1,1,1,1]])
    rk = ee.Kernel.fixed(7, 7, rect_w, 3, 3, False)
    dk = ee.Kernel.fixed(7, 7, diag_w, 3, 3, False)
    dir_mean = img.reduceNeighborhood(ee.Reducer.mean(), rk).updateMask(d.eq(1))
    dir_var = img.reduceNeighborhood(ee.Reducer.variance(), rk).updateMask(d.eq(1))
    dir_mean = dir_mean.addBands(img.reduceNeighborhood(ee.Reducer.mean(), dk).updateMask(d.eq(2)))
    dir_var = dir_var.addBands(img.reduceNeighborhood(ee.Reducer.variance(), dk).updateMask(d.eq(2)))
    for i in range(1, 4):
        dir_mean = dir_mean.addBands(img.reduceNeighborhood(ee.Reducer.mean(), rk.rotate(i)).updateMask(d.eq(2*i+1)))
        dir_var = dir_var.addBands(img.reduceNeighborhood(ee.Reducer.variance(), rk.rotate(i)).updateMask(d.eq(2*i+1)))
        dir_mean = dir_mean.addBands(img.reduceNeighborhood(ee.Reducer.mean(), dk.rotate(i)).updateMask(d.eq(2*i+2)))
        dir_var = dir_var.addBands(img.reduceNeighborhood(ee.Reducer.variance(), dk.rotate(i)).updateMask(d.eq(2*i+2)))
    dir_mean = dir_mean.reduce(ee.Reducer.sum())
    dir_var = dir_var.reduce(ee.Reducer.sum())
    varX = dir_var.subtract(dir_mean.multiply(dir_mean).multiply(sigmaV)).divide(sigmaV.add(1.0))
    b = varX.divide(dir_var)
    return dir_mean.add(b.multiply(img.subtract(dir_mean))).arrayFlatten([["sum"]])

# --- SIRAD multitemporal stack ---------------------------------------
s1 = (ee.ImageCollection("COPERNICUS/S1_GRD").filterBounds(aoi)
      .filter(ee.Filter.eq("instrumentMode", "IW"))
      .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))  # drop VV-only scenes
      .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))                 # one pass: fewer images, consistent geometry
      .select(["VV", "VH"]))                                                     # maskEdge dropped (connectedComponents too heavy for thumbnails)

def period(d1, d2, name):
    col = (s1.filterDate(d1, d2).select(POL)
           .sort("system:time_start", False).limit(40))   # cap to 40 most-recent scenes -> bound memory
    p = toDB(col.map(toNatural).mean())
    if USE_LEE:
        p = toDB(RefinedLee(toNatural(p)))
    else:
        p = p.focal_median(30, "circle", "meters")   # light despeckle (Lee too heavy for thumbnails)
    return p.rename(name)

p1 = period(DATES[0], DATES[1], "p1")
p2 = period(DATES[1], DATES[2], "p2")
p3 = period(DATES[2], DATES[3], "p3")

rgb = p1.addBands(p2).addBands(p3).clip(aoi)
# p2 -> p3 change (deforestation drops VH -> negative diff)
diff = toDB(toNatural(p3).divide(toNatural(p2))).rename("diff").clip(aoi)

RGB_VIS = {"bands": ["p1", "p2", "p3"], "min": -20, "max": -8, "gamma": 1.0}  # R=p1, G=p2, B=p3
NDVIpal = ["FFFFFF","CE7E45","DF923D","F1B555","FCD163","99B718","74A901","66A000",
           "529400","3E8601","207401","056201","004C00","023B01","012E01","011D01","011301"]
DIFF_VIS = {"bands": ["diff"], "min": -4, "max": 4, "palette": NDVIpal}

# --- export PNGs (with retry) + copy to remotion public/ -------------
PUBLIC = os.path.join(HERE, "remotion-sawah", "public")
def save(img, vis, name, dimensions=640, attempts=5):
    for a in range(attempts):
        try:
            url = img.visualize(**vis).getThumbURL(
                {"region": aoi, "dimensions": dimensions, "format": "png", "crs": "EPSG:3857"})
            r = requests.get(url, timeout=240)
            if r.status_code != 200:          # surface EE's real error message
                raise RuntimeError(f"{r.status_code}: {r.text[:220]}")
            out = os.path.join(HERE, name)
            with open(out, "wb") as f:
                f.write(r.content)
            os.makedirs(PUBLIC, exist_ok=True)
            shutil.copy(out, os.path.join(PUBLIC, name))
            print("Wrote", name, "(+ public/)")
            return
        except Exception as e:
            print("  retry", name, e); time.sleep(3 * (a + 1))
    print("  FAILED", name)

if __name__ == "__main__":
    print("Periods:", DATES, "| Lee:", USE_LEE)
    print("Preview RGB:", rgb.visualize(**RGB_VIS).getThumbURL(
        {"region": aoi, "dimensions": 700, "crs": "EPSG:3857"}))
    save(rgb, RGB_VIS, "sirad_konawe.png")
    save(diff, DIFF_VIS, "sirad_diff_konawe.png")
    print("\nRead the SIRAD RGB (R=period1, G=period2, B=period3 mean VH):")
    print("  WHITE/grey = forest intact across all periods (high VH everywhere) = stable")
    print("  YELLOW (R+G) = forest until period 3, cleared RECENTLY (T3->T4)")
    print("  RED (R only) = cleared EARLIER (around T2->T3)")
    print("  DARK = bare/mine throughout (already gone before T1)")
    print("  diff map: warm tones = VH dropped p2->p3 = fresh forest->mine.")
