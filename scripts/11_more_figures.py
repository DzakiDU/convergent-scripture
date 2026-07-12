#!/usr/bin/env python3
"""Three more figures:
   fig13  two-layer scatter: translation similarity vs fatwa distance per country-pair
   fig14  Southeast Asia choropleth coloured by mean fatwa strictness (plotly)
   fig15  verse x edition-pair cosine heatmap (105 verses x 10 pairs)
"""
import os, csv
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "data", "out"); FIG = os.path.join(OUT, "figs")
plt.rcParams["font.family"] = "DejaVu Sans"

# ---------- load translation similarity matrix ----------
raw = list(csv.reader(open(os.path.join(OUT, "lang_similarity_matrix.csv"))))
hdr = raw[0][1:]
S = {}
for r in raw[1:]:
    for j, v in enumerate(r[1:]): S[(r[0], hdr[j])] = float(v)

# ---------- load fatwa strictness vectors ----------
fat = {}
for r in csv.DictReader(open(os.path.join(ROOT, "data", "fatwa_comparison.csv"), encoding="utf-8")):
    fat.setdefault(r["country"], {})[r["issue"]] = int(r["strictness_1to5"])
ISSUES = ["Bank interest", "Insurance/takaful", "Crypto", "Tawarruq"]

# ============ fig13: two-layer scatter ============
# pairs with BOTH a translation edition and fatwa data: Indonesia/Malaysia/Brunei
lang = {"Indonesia": "id", "Malaysia": "ms", "Brunei": "bn"}
pairs = [("Indonesia", "Malaysia"), ("Indonesia", "Brunei"), ("Malaysia", "Brunei")]
xs, ys, labs = [], [], []
for a, b in pairs:
    tc = S[(lang[a], lang[b])]
    fd = np.mean([abs(fat[a][i] - fat[b][i]) for i in ISSUES])
    xs.append(tc); ys.append(fd); labs.append(f"{a}–{b}")

fig, ax = plt.subplots(figsize=(8, 6))
ax.axhspan(1.5, 2.6, xmin=0.55, color="#fdecea", zorder=0)
ax.scatter(xs, ys, s=260, c=["#4c78a8", "#59a14f", "#e15759"], edgecolor="white", linewidth=1.5, zorder=3)
for x, y, l in zip(xs, ys, labs):
    ax.annotate(l, (x, y), xytext=(0, 14), textcoords="offset points", ha="center", fontsize=11, weight="bold")
ax.annotate("Most similar translations,\nopposite rulings",
            xy=(xs[2], ys[2]), xytext=(0.885, 1.05), fontsize=10, color="#b2182b",
            arrowprops=dict(arrowstyle="->", color="#b2182b"))
ax.annotate("Similar translations,\nsimilar rulings", xy=(xs[1], ys[1]), xytext=(0.862, 0.75),
            fontsize=10, color="#1b7837", ha="left",
            arrowprops=dict(arrowstyle="->", color="#1b7837"))
ax.set_xlabel("Translation similarity (LaBSE mean cosine)", fontsize=12)
ax.set_ylabel("Fatwa distance (mean strictness gap, 4 issues)", fontsize=12)
ax.set_title("Two layers decouple: translation similarity does not predict fatwa distance", fontsize=12.5)
ax.set_xlim(0.86, 0.95); ax.set_ylim(-0.3, 3.0)
ax.text(0.86, -0.75, "n = 3 country-pairs with both a translation edition and fatwa data "
        "(Singapore, Thailand, the Philippines lack one layer).", fontsize=8, color="grey", transform=ax.get_yaxis_transform() if False else ax.transData)
ax.grid(alpha=.25)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig13_twolayer_scatter.png"), dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)

# ============ fig14: Southeast Asia choropleth ============
import plotly.express as px
iso = {"Indonesia": "IDN", "Malaysia": "MYS", "Singapore": "SGP", "Brunei": "BRN"}
dfc = pd.DataFrame([{"country": c, "iso": iso[c],
                     "strictness": np.mean([fat[c][i] for i in ISSUES])}
                    for c in ["Indonesia", "Malaysia", "Singapore", "Brunei"]])
figp = px.choropleth(dfc, locations="iso", color="strictness", hover_name="country",
                     color_continuous_scale="Reds", range_color=[1, 5],
                     labels={"strictness": "mean fatwa strictness"})
figp.update_geos(lataxis_range=[-11, 21], lonaxis_range=[93, 128], visible=True,
                 showcountries=True, countrycolor="grey", showland=True, landcolor="#f5f5f5")
figp.update_layout(title="Mean muʿāmalāt fatwa strictness across Southeast Asia (1 permissive – 5 strict)",
                   title_font_size=14, margin=dict(l=0, r=0, t=40, b=0), width=900, height=650)
figp.write_image(os.path.join(FIG, "fig14_sea_choropleth.png"), scale=2)

# ============ fig15: verse x pair cosine heatmap ============
pw = pd.read_csv(os.path.join(OUT, "pairwise_long.csv"))
mat = pw.pivot(index="surah_ayat", columns="pair", values="cosine")
# order rows by mean similarity (ascending -> most divergent on top)
mat = mat.loc[mat.mean(axis=1).sort_values().index]
plab = {"id-ms":"ID-MY","id-th":"ID-TH","id-tl":"ID-PH","id-bn":"ID-BN","ms-th":"MY-TH",
        "ms-tl":"MY-PH","ms-bn":"MY-BN","th-tl":"TH-PH","th-bn":"TH-BN","tl-bn":"PH-BN"}
order = ["id-ms","id-bn","ms-bn","id-th","id-tl","ms-th","ms-tl","th-bn","tl-bn","th-tl"]
mat = mat[order]; mat.columns = [plab[c] for c in order]
fig, ax = plt.subplots(figsize=(8.5, 12))
sns.heatmap(mat, cmap="mako_r", vmin=0.55, vmax=1.0, ax=ax,
            cbar_kws={"label": "cosine (dark = more similar)", "shrink": .5},
            yticklabels=[f"Q{v}" for v in mat.index])
ax.set_xlabel("edition pair"); ax.set_ylabel("verse (most divergent at top)")
ax.set_title("Where the editions disagree: cosine per verse × edition pair", fontsize=12)
plt.setp(ax.get_yticklabels(), fontsize=7)
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig15_verse_pair_heatmap.png"), dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)

print("DONE: fig13_twolayer_scatter.png, fig14_sea_choropleth.png, fig15_verse_pair_heatmap.png")
print("scatter points:", list(zip(labs, [round(x,3) for x in xs], [round(y,2) for y in ys])))
