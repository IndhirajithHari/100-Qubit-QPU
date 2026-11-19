#!/usr/bin/env python3
"""
Renders a photorealistic cleanroom optical micrograph & 3D packaging view
of the 100-Qubit Heavy-Hex QPU die inside its gold-plated carrier fixture.
Outputs build/qpu_100q_cleanroom_photomicrograph.png
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap

SPEC_PATH = "specs/qpu_heavyhex_40mm.json"
if not os.path.exists(SPEC_PATH):
    SPEC_PATH = "qpu-100q-heavyhex-40mm/specs/qpu_heavyhex_40mm.json"

with open(SPEC_PATH, "r") as f:
    spec = json.load(f)

qubits = spec["heavy_hex_lattice"]["qubits"]
qubit_dict = {q["id"]: q for q in qubits}
readout_pads = spec["readout_system"]["perimeter_pads"]
drive_pads = spec["xy_drive_routing"]["perimeter_pads"]

fig = plt.figure(figsize=(18, 14), dpi=300)
fig.patch.set_facecolor('#050811')

# Grid layout: Main cleanroom photomicrograph on left (10x14), two detailed zooms on right (8x7 each)
gs = fig.add_gridspec(2, 2, width_ratios=[1.3, 1.0], height_ratios=[1, 1], wspace=0.18, hspace=0.22)

ax_main = fig.add_subplot(gs[:, 0])
ax_zoom1 = fig.add_subplot(gs[0, 1])
ax_zoom2 = fig.add_subplot(gs[1, 1])

# =========================================================
# MAIN AXIS: Realistic Optical Cleanroom View
# =========================================================
ax_main.set_facecolor('#090d16')
ax_main.set_title("Cleanroom Photomicrograph: 100-Qubit QPU Mounted in Cryo Carrier Puck", 
                  color='#f8fafc', fontsize=12, fontweight='bold', pad=12)

# 1. Gold-plated OFHC Copper Carrier Puck (-6 to 46 mm)
puck = patches.FancyBboxPatch((-5.5, -5.5), 51.0, 51.0, boxstyle="round,pad=0.5,rounding_size=2.0",
                             facecolor='#b45309', edgecolor='#f59e0b', linewidth=2.5, alpha=0.95)
ax_main.add_patch(puck)

# 4 Corner mounting screw holes (M2 brass screws)
for sx, sy in [(-3.5, -3.5), (43.5, -3.5), (-3.5, 43.5), (43.5, 43.5)]:
    ax_main.add_patch(patches.Circle((sx, sy), 1.8, facecolor='#1e293b', edgecolor='#d97706', linewidth=1.5))
    ax_main.add_patch(patches.Circle((sx, sy), 1.0, facecolor='#d97706', edgecolor='#b45309', linewidth=1.0))
    # Screw slot
    ax_main.plot([sx - 0.7, sx + 0.7], [sy - 0.7, sy + 0.7], color='#78350f', lw=1.8)

# 2. Rogers RO4350B Carrier PCB Frame (ENIG gold immersion finish)
pcb = patches.Rectangle((-2.5, -2.5), 45.0, 45.0, facecolor='#14532d', edgecolor='#d97706', linewidth=1.5, alpha=0.9)
ax_main.add_patch(pcb)

# 3. Recessed Pocket Cutout (-0.15 to 40.15 mm = 40.3 mm pocket)
pocket = patches.Rectangle((-0.15, -0.15), 40.3, 40.3, facecolor='#020617', edgecolor='#ca8a04', linewidth=1.2)
ax_main.add_patch(pocket)

# 4. 40 mm x 40 mm High-Resistivity Silicon Die (Deep iridescent blue-gray mirror finish)
si_die = patches.Rectangle((0, 0), 40, 40, facecolor='#0f172a', edgecolor='#0284c7', linewidth=1.5, alpha=0.98)
ax_main.add_patch(si_die)

# Subtle wafer reflection gradient overlay
x_grad = np.linspace(0, 40, 100)
y_grad = np.linspace(0, 40, 100)
Xg, Yg = np.meshgrid(x_grad, y_grad)
Zg = np.sin((Xg + Yg) / 12.0) * 0.05 + 0.95
ax_main.imshow(Zg, extent=[0, 40, 0, 40], cmap='Blues', alpha=0.08, origin='lower', zorder=2)

# 5. Box-Mode Ground Isolation Moats (Etch lines in superconducting Al)
for i in range(1, 8):
    ax_main.axvline(i * 5.0, color='#0284c7', linewidth=0.5, alpha=0.45, zorder=3)
    ax_main.axhline(i * 5.0, color='#0284c7', linewidth=0.5, alpha=0.45, zorder=3)

# 6. Stepper Stitching Axes (x=20, y=20 mm)
ax_main.axvline(20.0, color='#f59e0b', linewidth=0.8, linestyle='-.', alpha=0.6, zorder=3)
ax_main.axhline(20.0, color='#f59e0b', linewidth=0.8, linestyle='-.', alpha=0.6, zorder=3)

# 7. 28 mm x 28 mm Core Boundary
core_box = patches.Rectangle((6, 6), 28, 28, fill=False, edgecolor='#38bdf8', linewidth=1.2, linestyle='--', alpha=0.8, zorder=3)
ax_main.add_patch(core_box)

# 8. Render 100 Transmon Qubits & Couplers (Shimmering metallic silver/aluminum)
for q in qubits:
    q1 = q
    for n in q["neighbors"]:
        if q["id"] < n:
            q2 = qubit_dict[n]
            ax_main.plot([q1["x_um"]/1000.0, q2["x_um"]/1000.0], 
                         [q1["y_um"]/1000.0, q2["y_um"]/1000.0], 
                         color='#e2e8f0', linewidth=0.9, alpha=0.75, zorder=4)

freq_sheen = {"f_A": "#38bdf8", "f_B": "#f472b6", "f_C": "#34d399"}
for q in qubits:
    xc = q["x_um"] / 1000.0
    yc = q["y_um"] / 1000.0
    # Capacitor pad pair in silver-blue metallic
    ax_main.add_patch(patches.Rectangle((xc - 0.21, yc + 0.008), 0.42, 0.16, color='#f1f5f9', alpha=0.95, zorder=5))
    ax_main.add_patch(patches.Rectangle((xc - 0.21, yc - 0.168), 0.42, 0.16, color='#f1f5f9', alpha=0.95, zorder=5))
    # Glowing center frequency marker dot
    ax_main.scatter(xc, yc, s=6, color=freq_sheen[q["freq_band"]], zorder=6)

# 9. 120 Perimeter Oversized GSG Launchers with Dual Wire Bonds
# Top & Bottom Readout Launchers (20 pads)
for p in readout_pads:
    xc = p["x_um"] / 1000.0
    yc = p["y_um"] / 1000.0
    # Die signal pad (silver)
    ax_main.add_patch(patches.Rectangle((xc - 0.15, yc - 0.175), 0.30, 0.35, color='#cbd5e1', zorder=7))
    # PCB matching pad (gold)
    y_pcb = 41.2 if p["edge"] == "TOP" else -1.2
    ax_main.add_patch(patches.Rectangle((xc - 0.15, y_pcb - 0.25), 0.30, 0.50, color='#eab308', zorder=7))
    # Dual wedge wire bonds spanning the 150 um gap
    y_die_edge = yc + 0.175 if p["edge"] == "TOP" else yc - 0.175
    y_pcb_edge = 40.4 if p["edge"] == "TOP" else -0.4
    ax_main.plot([xc - 0.05, xc - 0.05], [y_die_edge, y_pcb_edge], color='#ffffff', lw=1.2, zorder=8)
    ax_main.plot([xc + 0.05, xc + 0.05], [y_die_edge, y_pcb_edge], color='#ffffff', lw=1.2, zorder=8)

# Left & Right Drive Launchers (100 pads)
for p in drive_pads:
    xc = p["x_um"] / 1000.0
    yc = p["y_um"] / 1000.0
    ax_main.add_patch(patches.Rectangle((xc - 0.175, yc - 0.15), 0.35, 0.30, color='#cbd5e1', zorder=7))
    x_pcb = -1.2 if p["edge"] == "LEFT" else 41.2
    ax_main.add_patch(patches.Rectangle((x_pcb - 0.25, yc - 0.15), 0.50, 0.30, color='#eab308', zorder=7))
    x_die_edge = xc - 0.175 if p["edge"] == "LEFT" else xc + 0.175
    x_pcb_edge = -0.4 if p["edge"] == "LEFT" else 40.4
    ax_main.plot([x_die_edge, x_pcb_edge], [yc - 0.05, yc - 0.05], color='#ffffff', lw=1.0, zorder=8)
    ax_main.plot([x_die_edge, x_pcb_edge], [yc + 0.05, yc + 0.05], color='#ffffff', lw=1.0, zorder=8)

ax_main.set_xlim(-6.5, 46.5)
ax_main.set_ylim(-6.5, 46.5)
ax_main.set_xlabel("X Dimension (mm)", color='#94a3b8', fontsize=9)
ax_main.set_ylabel("Y Dimension (mm)", color='#94a3b8', fontsize=9)
ax_main.tick_params(colors='#64748b', labelsize=8)

# Annotations on main
ax_main.text(20, -4.5, "Gold-Plated OFHC Copper Housing Bracket", color='#f59e0b', fontsize=8.5, ha='center', fontweight='bold')
ax_main.text(20, 39.3, "10 Top Readout Ports", color='#f8fafc', fontsize=7.5, ha='center', fontweight='bold')
ax_main.text(20, 0.7, "10 Bottom Readout Ports", color='#f8fafc', fontsize=7.5, ha='center', fontweight='bold')
ax_main.text(0.7, 20, "50 Left Drive Lines", color='#f8fafc', fontsize=7.5, ha='left', va='center', rotation=90, fontweight='bold')
ax_main.text(39.3, 20, "50 Right Drive Lines", color='#f8fafc', fontsize=7.5, ha='right', va='center', rotation=-90, fontweight='bold')

# =========================================================
# ZOOM 1: Optical Micrograph of Heavy-Hex Unit Cell
# =========================================================
ax_zoom1.set_facecolor('#0b1120')
ax_zoom1.set_title("Optical Micrograph Zoom: 6-Qubit Heavy-Hex Unit Cell", color='#f8fafc', fontsize=10.5, fontweight='bold', pad=10)

# Cell around Q24, Q25, Q34, Q35, Q44, Q45 (center ~16 mm, 16 mm)
cell_qids = [24, 25, 34, 35, 44, 45]
for qid in cell_qids:
    q = qubit_dict[qid]
    xc, yc = q["x_um"], q["y_um"]
    fc = freq_sheen[q["freq_band"]]
    
    # Silicon substrate pocket opening
    ax_zoom1.add_patch(patches.Rectangle((xc - 245, yc - 203), 490, 406, facecolor='#020617', edgecolor='#1e293b', lw=1.2))
    # Superconducting Aluminum Capacitor Pads (Silver specular gradient)
    ax_zoom1.add_patch(patches.Rectangle((xc - 210, yc + 8), 420, 160, facecolor='#f8fafc', edgecolor='#cbd5e1', lw=1.0))
    ax_zoom1.add_patch(patches.Rectangle((xc - 210, yc - 168), 420, 160, facecolor='#f8fafc', edgecolor='#cbd5e1', lw=1.0))
    # Josephson Junction bridge
    ax_zoom1.add_patch(patches.Rectangle((xc - 3, yc - 8), 6, 16, facecolor='#93c5fd'))
    
    ax_zoom1.text(xc, yc + 225, f"Q{qid} ({q['freq_band']} = {q['f_01_GHz']} GHz)", 
                  color='#f8fafc', fontsize=7.5, ha='center', fontweight='bold')

# Inter-qubit planar coupling buses
for qid in cell_qids:
    q1 = qubit_dict[qid]
    for n in q1["neighbors"]:
        if n in cell_qids and qid < n:
            q2 = qubit_dict[n]
            ax_zoom1.plot([q1["x_um"], q2["x_um"]], [q1["y_um"], q2["y_um"]], color='#38bdf8', lw=2.5, zorder=4)
            mx, my = (q1["x_um"] + q2["x_um"])/2.0, (q1["y_um"] + q2["y_um"])/2.0
            ax_zoom1.text(mx + 25, my + 25, "J/2pi = 3.2 MHz", color='#38bdf8', fontsize=6.5, fontstyle='italic')

# Readout bus segment
ax_zoom1.plot([13500 + 250, 13500 + 250], [13000, 19000], color='#f43f5e', lw=2.5, label="50-Ohm Readout Bus")
ax_zoom1.plot([16100 + 250, 16100 + 250], [13000, 19000], color='#f43f5e', lw=2.5)

# Staggered notch resonators
for qid in cell_qids:
    q = qubit_dict[qid]
    x_bus = (8300.0 + q["col"] * 2600.0) + (250.0 if q["col"] < 5 else -250.0)
    ax_zoom1.plot([q["x_um"] + 225, x_bus], [q["y_um"], q["y_um"]], color='#f59e0b', lw=1.8, linestyle=':')
    ax_zoom1.text((q["x_um"] + x_bus)/2, q["y_um"] - 80, f"lambda/4 ({q['readout_freq_GHz']} GHz)", color='#fbbf24', fontsize=6.0, ha='center')

ax_zoom1.set_xlim(12800, 19200)
ax_zoom1.set_ylim(12800, 19200)
ax_zoom1.set_xlabel("X Position (um)", color='#94a3b8', fontsize=8.5)
ax_zoom1.set_ylabel("Y Position (um)", color='#94a3b8', fontsize=8.5)
ax_zoom1.tick_params(colors='#64748b', labelsize=7.5)
ax_zoom1.grid(color='#1e293b', linestyle=':', lw=0.5)

# =========================================================
# ZOOM 2: Die-to-PCB Dual-Wedge Wire Bond Interface
# =========================================================
ax_zoom2.set_facecolor('#0b1120')
ax_zoom2.set_title("SEM / Macro Zoom: Dual-Wedge Bond Transition across 150 um Gap", color='#f8fafc', fontsize=10.5, fontweight='bold', pad=10)

# Left side: Rogers RO4350B PCB (x from 0 to 1000 um)
ax_zoom2.add_patch(patches.Rectangle((0, 0), 1000, 4000, facecolor='#14532d', alpha=0.9)) # Green solder mask
# PCB Gold Pads (ENIG gold: #eab308)
ax_zoom2.add_patch(patches.Rectangle((400, 1850), 550, 300, facecolor='#eab308', edgecolor='#ca8a04', lw=1.5)) # Signal pad
ax_zoom2.text(675, 2000, "PCB SIGNAL PAD\n(ENIG Gold 50-Ohm)", color='#422006', fontsize=7.5, ha='center', va='center', fontweight='bold')

ax_zoom2.add_patch(patches.Rectangle((400, 2265), 550, 350, facecolor='#ca8a04', edgecolor='#a16207', lw=1.2)) # Ground pad top
ax_zoom2.add_patch(patches.Rectangle((400, 1385), 550, 350, facecolor='#ca8a04', edgecolor='#a16207', lw=1.2)) # Ground pad bot

# The 150 um Recessed Pocket Expansion Gap (x from 1000 to 1150 um)
ax_zoom2.add_patch(patches.Rectangle((1000, 0), 150, 4000, facecolor='#020617'))
ax_zoom2.annotate("", xy=(1000, 3700), xytext=(1150, 3700), arrowprops=dict(arrowstyle="<->", color="#facc15", lw=1.5))
ax_zoom2.text(1075, 3850, "150 um Gap\n(Expands to 205 um at 10 mK)", color="#facc15", fontsize=7.0, ha='center', fontweight='bold')

# Right side: Silicon Die Perimeter (x from 1150 to 3000 um)
ax_zoom2.add_patch(patches.Rectangle((1150, 0), 1850, 4000, facecolor='#0f172a')) # Dark Silicon
# Die Ground plane metal
ax_zoom2.add_patch(patches.Rectangle((1150, 0), 1850, 4000, facecolor='#1e293b', alpha=0.85))

# Die Signal Pad: 300 x 350 um (x from 1350 to 1700, y from 1850 to 2150)
ax_zoom2.add_patch(patches.Rectangle((1350, 1850), 350, 300, facecolor='#f8fafc', edgecolor='#cbd5e1', lw=1.5))
ax_zoom2.text(1525, 2000, "DIE SIGNAL PAD\n300 x 350 um\n(Al Thin-Film)", color='#0f172a', fontsize=7.5, ha='center', va='center', fontweight='bold')

# Die Ground Stitching Pads: 350 x 350 um
ax_zoom2.add_patch(patches.Rectangle((1350, 2265), 350, 350, facecolor='#94a3b8', edgecolor='#64748b', lw=1.2))
ax_zoom2.add_patch(patches.Rectangle((1350, 1385), 350, 350, facecolor='#94a3b8', edgecolor='#64748b', lw=1.2))

# 115 um lateral coplanar gaps
ax_zoom2.annotate("", xy=(1650, 2150), xytext=(1650, 2265), arrowprops=dict(arrowstyle="<->", color="#38bdf8", lw=1.2))
ax_zoom2.text(1720, 2207, "115 um Gap", color="#38bdf8", fontsize=6.5, va='center')

# 250 um coplanar taper to 20 um CPW trace
taper = patches.Polygon([(1700, 1850), (1700, 2150), (1950, 2010), (1950, 1990)], facecolor='#f8fafc')
ax_zoom2.add_patch(taper)
ax_zoom2.add_patch(patches.Rectangle((1950, 1990), 800, 20, facecolor='#f8fafc'))
ax_zoom2.text(2150, 2025, "20 um CPW (50-Ohm)", color='#f8fafc', fontsize=7.0)

# DUAL ULTRASONIC WEDGE WIRE BONDS (25 um Al-1%Si wire)
# Wedge bond heels (ellipses) and curving wire loop highlights
for y_bond in [1950, 2050]:
    # PCB wedge bond heel
    ax_zoom2.add_patch(patches.Ellipse((850, y_bond), 60, 35, facecolor='#e2e8f0', edgecolor='#0284c7', lw=1.5))
    # Die wedge bond heel
    ax_zoom2.add_patch(patches.Ellipse((1430, y_bond), 60, 35, facecolor='#e2e8f0', edgecolor='#0284c7', lw=1.5))
    # Ultrasonic wire bond shadow & bright wire
    ax_zoom2.plot([850, 1430], [y_bond - 8, y_bond - 8], color='#020617', lw=3.0, alpha=0.5)
    ax_zoom2.plot([850, 1430], [y_bond, y_bond], color='#ffffff', lw=3.2, solid_capstyle='round')
    ax_zoom2.plot([850, 1430], [y_bond + 2, y_bond + 2], color='#38bdf8', lw=1.0, alpha=0.8)

# Ground wedge bonds
for yg in [1500, 1620, 2380, 2500]:
    ax_zoom2.add_patch(patches.Ellipse((850, yg), 55, 30, facecolor='#cbd5e1', edgecolor='#059669', lw=1.2))
    ax_zoom2.add_patch(patches.Ellipse((1430, yg), 55, 30, facecolor='#cbd5e1', edgecolor='#059669', lw=1.2))
    ax_zoom2.plot([850, 1430], [yg, yg], color='#cbd5e1', lw=2.5, solid_capstyle='round')

ax_zoom2.text(1140, 2120, "Dual 25 um Wedge Bonds\n(220 um Loop Height; Leff ~ 0.20 nH)", 
              color='#ffffff', fontsize=7.5, ha='center', fontweight='bold',
              bbox=dict(boxstyle='round,pad=0.3', facecolor='#0369a1', alpha=0.85, edgecolor='#38bdf8'))

ax_zoom2.set_xlim(200, 2800)
ax_zoom2.set_ylim(1100, 2900)
ax_zoom2.set_xlabel("X Position (um)", color='#94a3b8', fontsize=8.5)
ax_zoom2.set_ylabel("Y Position (um)", color='#94a3b8', fontsize=8.5)
ax_zoom2.tick_params(colors='#64748b', labelsize=7.5)
ax_zoom2.grid(color='#1e293b', linestyle=':', lw=0.5)

# Save figure
OUT_PATH = "build/qpu_100q_cleanroom_photomicrograph.png"
plt.savefig(OUT_PATH, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print(f"[Render] Cleanroom Photomicrograph saved successfully to {OUT_PATH}")
