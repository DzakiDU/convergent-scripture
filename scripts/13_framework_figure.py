#!/usr/bin/env python3
"""Figure: the conceptual chain from scripture to fatwa (grayscale, print-safe).
Arabic text -> tafsir -> translation -> usul al-fiqh -> maqasid -> fatwa.
Encodes the paper's argument: left = convergence (measured), right = divergence
(measured outcome), middle = juristic mechanism (theorized); bold border marks
what the study measures; four extratextual forces feed the ruling.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams["font.family"] = "DejaVu Sans"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "data", "out", "figs")

# grayscale palette
ZA, ZB = "#efefef", "#d9d9d9"          # convergence / divergence zones
EDGE, EDGE_M = "#8a8a8a", "#111111"    # normal / measured box border
INK, SUB, ARR = "#111111", "#555555", "#444444"

fig, ax = plt.subplots(figsize=(9.0, 3.6))
ax.set_xlim(0, 830); ax.set_ylim(320, 0); ax.axis("off")

# title
ax.text(415, 30, "The conceptual chain from scripture to fatwa",
        ha="center", fontsize=15, fontweight="bold", color=INK)

# zones
ax.add_patch(Rectangle((8, 66), 392, 150, facecolor=ZA, edgecolor="none"))
ax.add_patch(Rectangle((424, 66), 398, 150, facecolor=ZB, edgecolor="none"))
ax.text(204, 86, "CONVERGENCE", ha="center", fontsize=12, fontweight="bold", color=INK)
ax.text(204, 103, "translations barely differ across states", ha="center", fontsize=10, color=SUB)
ax.text(623, 86, "DIVERGENCE", ha="center", fontsize=12, fontweight="bold", color=INK)
ax.text(623, 103, "the same text yields different rulings", ha="center", fontsize=10, color=SUB)

# chain arrows
for x1, x2 in [(136, 151), (264, 279), (392, 439), (552, 570), (683, 701)]:
    ax.annotate("", xy=(x2, 167), xytext=(x1, 167),
                arrowprops=dict(arrowstyle="-|>", color=ARR, lw=1.8))

def box(x, title, sub, measured=False):
    ax.add_patch(Rectangle((x, 130), 112, 72, facecolor="white",
                 edgecolor=EDGE_M if measured else EDGE, linewidth=2.4 if measured else 1.3))
    cx = x + 56
    ax.text(cx, 159, title, ha="center", va="center", fontsize=11, fontweight="bold", color=INK)
    ax.text(cx, 181, sub, ha="center", va="center", fontsize=9.5,
            color=INK if measured else SUB, fontweight="bold" if measured else "normal",
            style="normal" if measured else "italic")

box(24,  "Arabic text",  "invariant")
box(152, "Tafsir",       "exegesis")
box(280, "Translation",  "measured", measured=True)
box(440, "Usul al-fiqh", "istinbat")
box(571, "Maqasid",      "objectives")
box(702, "Fatwa",        "measured", measured=True)

# legend
ax.add_patch(Rectangle((22, 250), 22, 11, facecolor=ZA, edgecolor="#bbb"))
ax.text(50, 259, "convergence (measured baseline)", fontsize=10, color=SUB, va="center")
ax.add_patch(Rectangle((300, 250), 22, 11, facecolor=ZB, edgecolor="#bbb"))
ax.text(328, 259, "divergence (measured outcome)", fontsize=10, color=SUB, va="center")
ax.add_patch(Rectangle((560, 250), 22, 11, facecolor="white", edgecolor=EDGE_M, linewidth=2.2))
ax.text(588, 259, "bold border = what we measure", fontsize=10, color=SUB, va="center")

fig.tight_layout(pad=0.4)
fig.savefig(os.path.join(FIG, "fig0_framework_chain.png"), dpi=200, bbox_inches="tight", facecolor="white")
print("DONE: fig0_framework_chain.png")
