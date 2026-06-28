#!/usr/bin/env python3
"""
Search (and optionally download) PlanetScope scenes over the Konawe AOI
via the Planet Data API. Uses konawe_aoi.geojson as the search geometry.

API key (NOT hardcoded) — first found wins:
  1. env var  PL_API_KEY
  2. file     Credentials/planet.txt   (single line: the key)

Install:  pip install requests
Docs: https://developers.planet.com/docs/apis/data/

Usage:
  python social-media/planet_konawe_search.py            # search -> prints + planet_konawe_scenes.csv
  # then download specific scenes (edit IDS below or call download()):
  #   python -c "import planet_konawe_search as p; p.download(['20240115_0123_...'], 'ortho_visual')"
"""

import os
import sys
import csv
import json
import time
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
AOI_FILE = os.path.join(HERE, "konawe_aoi.geojson")
OUT_CSV = os.path.join(HERE, "planet_konawe_scenes.csv")
DL_DIR = os.path.join(HERE, "planet_konawe")          # downloads go here

# --- search params (edit freely) --------------------------------------
ITEM_TYPE = "PSScene"
START = "2017-01-01T00:00:00Z"
END = "2026-06-30T23:59:59Z"
MAX_CLOUD = 0.15                                       # 15%
ASSET_WANTED = "ortho_analytic_4b_sr"                 # require this asset be orderable
BASE = "https://api.planet.com/data/v1"

def get_key():
    k = os.environ.get("PL_API_KEY")
    if k:
        return k.strip()
    p = os.path.join(HERE, "..", "Credentials", "planet.txt")
    if os.path.exists(p):
        return open(p).read().strip()
    sys.exit("No Planet API key. Set PL_API_KEY or create Credentials/planet.txt")

def aoi_geometry():
    gj = json.load(open(AOI_FILE))
    return gj["features"][0]["geometry"]

def search():
    key = get_key()
    s = requests.Session(); s.auth = (key, "")
    flt = {"type": "AndFilter", "config": [
        {"type": "GeometryFilter", "field_name": "geometry", "config": aoi_geometry()},
        {"type": "DateRangeFilter", "field_name": "acquired",
         "config": {"gte": START, "lte": END}},
        {"type": "RangeFilter", "field_name": "cloud_cover", "config": {"lte": MAX_CLOUD}},
        {"type": "AssetFilter", "config": [ASSET_WANTED]},
    ]}
    body = {"item_types": [ITEM_TYPE], "filter": flt}
    r = s.post(f"{BASE}/quick-search", json=body); r.raise_for_status()

    rows = []
    page = r.json()
    while True:
        for f in page.get("features", []):
            p = f["properties"]
            rows.append({"id": f["id"], "acquired": p.get("acquired", "")[:10],
                         "cloud": round(p.get("cloud_cover", 0), 3),
                         "satellite": p.get("satellite_id", "")})
        nxt = page.get("_links", {}).get("_next")
        if not nxt:
            break
        page = s.get(nxt).json()

    rows.sort(key=lambda x: x["acquired"])
    with open(OUT_CSV, "w", newline="") as fcsv:
        w = csv.DictWriter(fcsv, fieldnames=["id", "acquired", "cloud", "satellite"])
        w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} scenes (cloud <= {MAX_CLOUD}) -> {OUT_CSV}")
    for x in rows[:40]:
        print(f"  {x['acquired']}  cloud={x['cloud']:<5}  {x['id']}")
    if len(rows) > 40:
        print(f"  ... +{len(rows)-40} more (see CSV)")
    return rows

def download(item_ids, asset_type="ortho_visual"):
    """Activate + download the given asset for each scene id into planet_konawe/."""
    key = get_key()
    s = requests.Session(); s.auth = (key, "")
    os.makedirs(DL_DIR, exist_ok=True)
    for iid in item_ids:
        url = f"{BASE}/item-types/{ITEM_TYPE}/items/{iid}/assets"
        assets = s.get(url).json()
        if asset_type not in assets:
            print(f"  {iid}: no '{asset_type}' (have: {list(assets)[:6]}...)"); continue
        a = assets[asset_type]
        if a["status"] != "active":                   # activate + poll
            s.get(a["_links"]["activate"])
            print(f"  {iid}: activating {asset_type} ...")
            while a["status"] != "active":
                time.sleep(10)
                a = s.get(url).json()[asset_type]
        loc = a["location"]
        out = os.path.join(DL_DIR, f"{iid}_{asset_type}.tif")
        with s.get(loc, stream=True) as resp:
            resp.raise_for_status()
            with open(out, "wb") as f:
                for chunk in resp.iter_content(1 << 20):
                    f.write(chunk)
        print("  downloaded", out)

if __name__ == "__main__":
    search()
    # To download: pick ids from the CSV, then e.g.
    # download(["20240115_xxxx_xxxx", "20170401_yyyy_yyyy"], "ortho_visual")
