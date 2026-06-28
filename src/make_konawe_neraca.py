#!/usr/bin/env python3
"""
"Neraca Pembangunan" infographic — an HONEST balance sheet for the Konawe nickel video.
Counters the "economy >> environment, so damage is OK" argument by:
  - flagging scope (econ figures are NATIONAL & gross; cost is LOCAL, this block)
  - adding carbon released (one-time) and the perpetual ESV as an asset (NPV)
  - noting who profits vs who pays
Real, sourced figures (+ stated assumptions for estimates).
-> konawe_neraca.png (square 1080, + remotion-konawe/public/).

Install:  pip install matplotlib
"""

import os
import shutil
import textwrap
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "konawe_neraca.png")
PUBLIC = os.path.join(HERE, "remotion-konawe", "public")

# --- figures + assumptions -------------------------------------------
AREA_HA = 6093                       # forest lost, Hansen 2001-2024 (this AOI)
ESV_PER_HA = 2700                    # tropical-forest ESV, $/ha/yr (Costanza 1997)
DISCOUNT = 0.05                      # for perpetuity NPV
CARBON_TC_HA = 200                   # tC/ha tropical forest (mid estimate)

ESV_LOST_M = AREA_HA * ESV_PER_HA / 1e6          # ~16  ($ juta/yr)
NPV_M = ESV_LOST_M / DISCOUNT                     # ~330 ($ juta, services as an asset)
CO2_MT = AREA_HA * CARBON_TC_HA * 3.67 / 1e6      # ~4.5 (juta ton CO2)
CO2_LO_M = CO2_MT * 20                             # $ juta @ $20/t
CO2_HI_M = CO2_MT * 50                             # $ juta @ $50/t

BG = "#0e1419"; INK = "#eef3f7"; SUB = "#9aa7b3"
GREEN = "#3ecf73"; GREEN_BG = "#13241b"
RED = "#ff6b5e"; RED_BG = "#241314"

EKON = [
    ("±60.000", "lapangan kerja — target Kawasan Morosi (bukan blok ini)", 0.745),
    ("$34,8 Miliar", "nilai tambah hilirisasi NASIONAL, 2020→23 (angka kotor)", 0.610),
]
EKON_TAG = "Sekali keruk — nikel habis dalam beberapa dekade."

COST = [
    (f"{AREA_HA:,} ha".replace(",", "."), "hutan hilang — blok ini (Hansen 2001–24)", 0.775),
    (f"~{CO2_MT:.1f} Jt ton CO₂".replace(".", ","),
     f"dilepas ≈ ${CO2_LO_M:.0f}–{CO2_HI_M:.0f} Jt (sekali, est.)", 0.650),
    (f"$16 Jt / th  →  ${NPV_M:.0f} Jt",
     "jasa ekosistem sbg aset — SELAMANYA", 0.525),
]
COST_TAG = "+ air, ikan, biodiversitas — banyak yang belum terhitung."

REFRAME = ("Bandingkan setara: angka ekonomi itu NASIONAL & kotor, sekali keruk. "
           "Ongkos ini LOKAL, berulang, selamanya — dan belum lengkap.")
WHOPAYS = ("Untung →  perusahaan & kas negara.        "
           "Ongkos →  warga, nelayan, generasi mendatang.")
SOURCES = ("Sumber: hutan — Hansen GFC 2001–24 · jasa ekosistem — Costanza 1997 & TEEB 2010 "
           "(NPV diskonto 5%) · karbon — asumsi 200 tC/ha, $20–50/t CO₂ · tenaga kerja — "
           "Kompas/Liputan6 2021 · ekspor & hilirisasi — Statista/AfDB/CSIS 2023.")


def panel(ax, x0, x1, header, stats, tag, accent, bg):
    ax.add_patch(FancyBboxPatch((x0, 0.40), x1 - x0, 0.46,
                 boxstyle="round,pad=0.012,rounding_size=0.022",
                 fc=bg, ec=accent, lw=2.5, transform=ax.transAxes, zorder=2))
    cx = (x0 + x1) / 2
    ax.text(cx, 0.832, header, ha="center", va="center", color=accent,
            fontsize=18, fontweight="bold", transform=ax.transAxes)
    for big, label, y in stats:
        ax.text(cx, y, big, ha="center", va="center", color=INK,
                fontsize=30, fontweight="bold", transform=ax.transAxes)
        ax.text(cx, y - 0.036, "\n".join(textwrap.wrap(label, 36)), ha="center", va="top",
                color=SUB, fontsize=11, transform=ax.transAxes, linespacing=1.15)
    ax.text(cx, 0.425, "\n".join(textwrap.wrap(tag, 40)), ha="center", va="bottom",
            color=SUB, fontsize=10.5, fontstyle="italic", transform=ax.transAxes, linespacing=1.15)


def main():
    fig, ax = plt.subplots(figsize=(10.8, 10.8))
    fig.patch.set_facecolor(BG)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); ax.set_facecolor(BG)

    ax.text(0.5, 0.955, "NERACA PEMBANGUNAN", ha="center", color=INK, fontsize=32, fontweight="bold")
    ax.text(0.5, 0.917, "Tambang Nikel · Konawe, Sulawesi Tenggara", ha="center", color=SUB, fontsize=15)

    # balance-beam motif
    ax.plot([0.22, 0.78], [0.882, 0.882], color="#8b98a5", lw=3, zorder=3,
            transform=ax.transAxes, solid_capstyle="round")
    for px in (0.22, 0.78):
        ax.plot([px, px], [0.882, 0.862], color="#8b98a5", lw=2, transform=ax.transAxes, zorder=3)
        ax.add_patch(plt.Circle((px, 0.857), 0.011, color="#8b98a5", transform=ax.transAxes, zorder=3))
    ax.add_patch(Polygon([[0.5, 0.882], [0.487, 0.85], [0.513, 0.85]], closed=True,
                 color="#8b98a5", transform=ax.transAxes, zorder=3))

    panel(ax, 0.05, 0.485, "MANFAAT EKONOMI", EKON, EKON_TAG, GREEN, GREEN_BG)
    panel(ax, 0.515, 0.95, "ONGKOS LINGKUNGAN", COST, COST_TAG, RED, RED_BG)

    # framing band: like-for-like reframe + who pays
    ax.add_patch(FancyBboxPatch((0.05, 0.205), 0.90, 0.165,
                 boxstyle="round,pad=0.01,rounding_size=0.02",
                 fc="#1b2330", ec="#3a4658", lw=1.2, transform=ax.transAxes, zorder=2))
    ax.text(0.5, 0.348, "\n".join(textwrap.wrap(REFRAME, 92)), ha="center", va="top",
            color=INK, fontsize=12.5, fontstyle="italic", transform=ax.transAxes, linespacing=1.2)
    ax.text(0.5, 0.232, WHOPAYS, ha="center", va="bottom", color="#cdd6df",
            fontsize=12, fontweight="bold", transform=ax.transAxes)

    ax.text(0.5, 0.135, "\n".join(textwrap.wrap(SOURCES, 118)), ha="center", va="top",
            color="#6f7b86", fontsize=8, transform=ax.transAxes)
    ax.text(0.5, 0.045, "@jalmiburung · citra satelit", ha="center", color="#5a6470",
            fontsize=9, transform=ax.transAxes)

    plt.savefig(OUT, dpi=100, facecolor=BG, bbox_inches="tight", pad_inches=0.2)
    print("Wrote", OUT, f"(CO2 {CO2_MT:.1f} Mt -> ${CO2_LO_M:.0f}-{CO2_HI_M:.0f}M; NPV ${NPV_M:.0f}M)")
    os.makedirs(PUBLIC, exist_ok=True)
    shutil.copy(OUT, os.path.join(PUBLIC, "konawe_neraca.png"))
    print("Copied to", os.path.join(PUBLIC, "konawe_neraca.png"))


if __name__ == "__main__":
    main()
