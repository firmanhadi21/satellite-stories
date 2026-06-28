#!/usr/bin/env python3
"""
SIRAD RESULT as a proper MAP: north arrow + scale bar + lat/lon coordinates + legend.
Reuses the SIRAD computation in gee_konawe_sirad.py (same AOI, periods, RGB).
Writes sirad_konawe_map.png (+ copies to remotion-sawah/public/).

Install:  pip install earthengine-api requests pillow numpy matplotlib
Run:      python social-media/gee_konawe_sirad_map.py
"""

import os
import io
import math
import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.patheffects as pe
from PIL import Image

import ee
import gee_konawe_sirad as sd          # initializes EE + builds aoi, rgb, RGB_VIS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sirad_konawe_map.png")
PUBLIC = os.path.join(HERE, "remotion-konawe", "public")

# --- AOI bounds in degrees (EPSG:4326, north up) ----------------------
coords = ee.List(sd.aoi.bounds().coordinates().get(0)).getInfo()
xs = [c[0] for c in coords]; ys = [c[1] for c in coords]
W, E, S, N = min(xs), max(xs), min(ys), max(ys)

# --- fetch the SIRAD RGB in lat/lon -----------------------------------
def fetch_rgb(dimensions=800, attempts=5):
    for a in range(attempts):
        try:
            url = sd.rgb.visualize(**sd.RGB_VIS).getThumbURL(
                {"region": sd.aoi, "dimensions": dimensions, "format": "png", "crs": "EPSG:4326"})
            r = requests.get(url, timeout=240)
            if r.status_code != 200:
                raise RuntimeError(f"{r.status_code}: {r.text[:200]}")
            return np.array(Image.open(io.BytesIO(r.content)).convert("RGB"))
        except Exception as e:
            print("  retry rgb:", e)
    raise SystemExit("Could not fetch SIRAD RGB.")

img = fetch_rgb()

# --- per-period forest loss (VH threshold proxy; matches the map colours) ---
FOREST_VH = -15.0          # dB: forest VH > this; bare/mine below (approximate)
def ha(mask):
    a = mask.multiply(ee.Image.pixelArea()).reduceRegion(
        ee.Reducer.sum(), sd.aoi, scale=30, maxPixels=int(1e13), tileScale=4)
    v = a.values().get(0)
    return (ee.Number(v).divide(1e4).getInfo() if v is not None else 0.0)
f1, f2, f3 = sd.p1.gt(FOREST_VH), sd.p2.gt(FOREST_VH), sd.p3.gt(FOREST_VH)
loss_18_20 = ha(f1.And(f2.Not()))    # red on the map
loss_20_26 = ha(f2.And(f3.Not()))    # yellow on the map
remain = ha(f3)                      # white on the map
print(f"Loss 2018-20: {loss_18_20:,.0f} ha | 2020-26: {loss_20_26:,.0f} ha | forest left 2026: {remain:,.0f} ha")

# --- plot the map -----------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 8.5))
ax.imshow(img, extent=[W, E, S, N], origin="upper", aspect="auto")
ax.set_title("SIRAD — Deteksi Perubahan Radar (Sentinel-1 VH)\n"
             "Tambang Nikel, Konawe  ·  R: 2017–18  G: 2018–20  B: 2020–26",
             fontsize=12, fontweight="bold")
ax.set_xlabel("Bujur (°E)"); ax.set_ylabel("Lintang (°)")
ax.tick_params(direction="out", length=4)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.2f}"))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.2f}"))
ax.grid(True, color="white", alpha=0.30, linestyle=":")

stroke = [pe.withStroke(linewidth=3, foreground="black")]

# north arrow (top-right)
ax.annotate("N", xy=(0.95, 0.93), xytext=(0.95, 0.83), xycoords="axes fraction",
            ha="center", va="center", fontsize=18, fontweight="bold", color="white",
            arrowprops=dict(arrowstyle="-|>", color="white", lw=2.5), path_effects=stroke)

# scale bar (bottom-left)
lat_c = (S + N) / 2.0
m_per_deg_lon = 111320.0 * math.cos(math.radians(lat_c))
bar_km = 2
bar_deg = bar_km * 1000.0 / m_per_deg_lon
x0 = W + (E - W) * 0.06
y0 = S + (N - S) * 0.06
ax.plot([x0, x0 + bar_deg], [y0, y0], color="white", lw=5, solid_capstyle="butt", path_effects=stroke)
ax.text(x0 + bar_deg / 2, y0 + (N - S) * 0.018, f"{bar_km} km", ha="center",
        color="white", fontweight="bold", fontsize=10, path_effects=stroke)

# legend (SIRAD colour code)
legend = [
    Patch(facecolor="white", edgecolor="k", label="Hutan utuh 2017–2026"),
    Patch(facecolor="#ffff66", edgecolor="k", label="Dibuka 2020–2026 (baru)"),
    Patch(facecolor="#ff5555", edgecolor="k", label="Dibuka 2018–2020"),
    Patch(facecolor="#1a1a1a", edgecolor="k", label="Sudah terbuka / tambang ≤2017"),
]
leg = ax.legend(handles=legend, loc="lower right", fontsize=8,
                title="SIRAD — kapan hutan dibuka", title_fontsize=9,
                framealpha=1.0, edgecolor="black", borderaxespad=1.0, labelspacing=0.6)
leg.get_frame().set_linewidth(1.2)
leg.set_zorder(5)        # keep it above the map, anchored in the lower-right corner

# infographic: per-period forest loss (inset bar chart, upper-left)
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
iax = inset_axes(ax, width="40%", height="26%", loc="upper left", borderpad=1.2)
iax.set_facecolor("white"); iax.patch.set_alpha(0.92)
iax.barh([0, 1], [loss_18_20, loss_20_26], color=["#ff5555", "#ffff66"],
         edgecolor="black", height=0.5)
iax.set_yticks([0, 1]); iax.set_yticklabels(["2018–20", "2020–26"], fontsize=7)
iax.set_ylim(-0.6, 2.0)                     # headroom so the title fits inside the box
iax.tick_params(labelsize=7)
for i, v in enumerate([loss_18_20, loss_20_26]):
    iax.text(v, i, f" {v:,.0f}", va="center", fontsize=7, fontweight="bold")
iax.set_xlim(0, max(loss_18_20, loss_20_26, 1) * 1.32)
iax.text(0.5, 0.95, "Hutan hilang (ha)", transform=iax.transAxes,   # title INSIDE the box
         ha="center", va="top", fontsize=8, fontweight="bold")

# summary + credit
fig.text(0.5, 0.028,
         f"Hutan tersisa 2026 ≈ {remain:,.0f} ha  ·  hilang 2018–2026 ≈ "
         f"{loss_18_20 + loss_20_26:,.0f} ha  (estimasi ambang VH)",
         ha="center", fontsize=8, fontweight="bold")
fig.text(0.5, 0.005, "Metode SIRAD (Doblas, ISA) · Sentinel-1 © ESA/Copernicus · @jalmiburung",
         ha="center", fontsize=7, color="gray")

plt.tight_layout()
plt.savefig(OUT, dpi=200, bbox_inches="tight")
print("Wrote", OUT)
os.makedirs(PUBLIC, exist_ok=True)
import shutil
shutil.copy(OUT, os.path.join(PUBLIC, "sirad_konawe_map.png"))
print("Copied to", os.path.join(PUBLIC, "sirad_konawe_map.png"))
