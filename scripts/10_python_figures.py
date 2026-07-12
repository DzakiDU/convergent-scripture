#!/usr/bin/env python3
"""Python figures (matplotlib/seaborn) that R could not do well:
   fig10  t-SNE semantic map of 105 verses x 5 editions (colour by edition | domain)
   fig11  seaborn clustermap of the 5x5 similarity matrix (dendrograms)
   fig12  Q83:1 close reading with correct Arabic script + 5 renderings
Advantage over R: proper diacritics (muʿāmalāt) and Arabic RTL rendering."""
import os, csv, re, unicodedata
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import seaborn as sns
from sklearn.manifold import TSNE
from sentence_transformers import SentenceTransformer
import arabic_reshaper
from bidi.algorithm import get_display

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG  = os.path.join(ROOT, "data", "out", "figs")
CSV  = os.path.join(ROOT, "data", "economic_verses_aligned.csv")

plt.rcParams["font.family"] = "DejaVu Sans"   # covers ʿ, ā diacritics
# locate an Arabic-capable font
AR = None
for c in ["/System/Library/Fonts/GeezaPro.ttc",
          "/System/Library/Fonts/Supplemental/Baghdad.ttc",
          "/System/Library/Fonts/Supplemental/DecoTypeNaskh.ttc",
          "/System/Library/Fonts/Supplemental/Al Nile.ttc"]:
    if os.path.exists(c): AR = fm.FontProperties(fname=c); break
TH_FONT = None
for c in ["/System/Library/Fonts/Thonburi.ttc",
          "/System/Library/Fonts/Supplemental/Ayuthaya.ttf",
          "/Library/Fonts/Thonburi.ttf"]:
    if os.path.exists(c): TH_FONT = fm.FontProperties(fname=c); break
HARAKAT = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭ]")

LANGS = ["id", "ms", "th", "tl", "bn"]
ED = {"id":"Indonesia", "ms":"Malaysia", "th":"Thailand", "tl":"Philippines", "bn":"Brunei"}
DOM_EN = {"riba":"Riba","mizan-timbangan-adil":"Measures","zakat-infaq":"Zakat/alms",
 "infaq-etika":"Spending","harta-anak-yatim":"Orphans","warisan-faraid":"Inheritance",
 "uqud-akad-janji":"Contracts","gharar-maysir-judi":"Gharar/gambling","bay-jualbeli":"Sale/trade",
 "amanah-trust":"Trust","penimbunan-kanz":"Hoarding","rezeki-kerja-halal":"Earning",
 "wasiat":"Bequest","harta-batil-suap":"Unlawful gain","distribusi-kekayaan":"Distribution",
 "ijarah":"Leasing","syirkah-mudharabah":"Partnership","produksi":"Production",
 "qard-utang":"Lending","harta-fitnah":"Wealth-trial"}

rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
ed_lab, dom_lab, verse_lab = [], [], []
for lg in LANGS:
    for r in rows:
        ed_lab.append(ED[lg]); dom_lab.append(DOM_EN.get(r["tema"], r["tema"])); verse_lab.append(r["surah_ayat"])
NPY = os.path.join(ROOT, "data", "out", "embeddings.npy")
if os.path.exists(NPY):
    X = np.load(NPY); print("Loaded cached embeddings")
else:
    print("Loading LaBSE (cached model)...")
    model = SentenceTransformer("sentence-transformers/LaBSE")
    vecs = []
    for lg in LANGS:
        E = model.encode([r[f"terjemah_{lg}"] for r in rows], normalize_embeddings=True, show_progress_bar=False)
        vecs.extend(list(E))
    X = np.array(vecs); np.save(NPY, X)

# ============ fig10: t-SNE (colour by edition | by domain) ============
ts = TSNE(n_components=2, perplexity=20, init="pca", learning_rate="auto", random_state=0).fit_transform(X)
fig, ax = plt.subplots(1, 2, figsize=(13, 5.6))
pal_ed = dict(zip(ED.values(), sns.color_palette("Set1", 5)))
for e in ED.values():
    m = [i for i in range(len(ed_lab)) if ed_lab[i] == e]
    ax[0].scatter(ts[m,0], ts[m,1], s=34, color=pal_ed[e], label=e, alpha=.8, edgecolor="white", linewidth=.4)
ax[0].set_title("Coloured by edition", fontsize=12)
ax[0].legend(fontsize=8, frameon=False, loc="best"); ax[0].set_xticks([]); ax[0].set_yticks([])
doms = sorted(set(dom_lab)); pal_d = dict(zip(doms, sns.color_palette("husl", len(doms))))
for d in doms:
    m = [i for i in range(len(dom_lab)) if dom_lab[i] == d]
    ax[1].scatter(ts[m,0], ts[m,1], s=34, color=pal_d[d], label=d, alpha=.8, edgecolor="white", linewidth=.4)
ax[1].set_title("Coloured by muʿāmalāt domain", fontsize=12)
ax[1].legend(fontsize=6.5, frameon=False, ncol=2, loc="upper left", bbox_to_anchor=(1.0, 1.0))
ax[1].set_xticks([]); ax[1].set_yticks([])
fig.suptitle("Semantic map of muʿāmalāt verse renderings (t-SNE of LaBSE embeddings, 105 verses × 5 editions)", fontsize=13)
fig.tight_layout(rect=[0,0,1,0.96])
fig.savefig(os.path.join(FIG, "fig10_tsne_semantic_map.png"), dpi=200, bbox_inches="tight")
plt.close(fig)

# ============ fig11: seaborn clustermap of similarity matrix ============
M = np.zeros((5,5))
simfile = os.path.join(ROOT, "data", "out", "lang_similarity_matrix.csv")
raw = list(csv.reader(open(simfile)))
hdr = raw[0][1:]
for i, r in enumerate(raw[1:]):
    for j, v in enumerate(r[1:]): M[i,j] = float(v)
labels = [ED[h] for h in hdr]
import pandas as pd
dfm = pd.DataFrame(M, index=labels, columns=labels)
g = sns.clustermap(dfm, cmap="mako_r", annot=True, fmt=".2f", figsize=(6.8,6.8),
                   vmin=0.65, vmax=1.0, linewidths=1, cbar_kws={"label":"cosine"},
                   annot_kws={"size":11})
g.fig.suptitle("Cross-edition similarity with clustering (LaBSE mean cosine)", y=1.02, fontsize=12)
g.savefig(os.path.join(FIG, "fig11_clustermap.png"), dpi=200, bbox_inches="tight")
plt.close(g.fig)

# ============ fig12: Q83:1 close reading with Arabic ============
q = {r["surah_ayat"]: r for r in rows}["83:1"]
def arabic(t):
    bare = "".join(c for c in t if not unicodedata.combining(c))
    return get_display(arabic_reshaper.reshape(bare))
fig, ax = plt.subplots(figsize=(10, 6.4)); ax.axis("off")
ax.text(0.5, 0.95, "Close reading — Q 83:1  (wayl li-l-muṭaffifīn)", ha="center", fontsize=15, weight="bold")
if AR:
    ax.text(0.5, 0.83, arabic(q["arabic"]), ha="center", fontsize=30, fontproperties=AR)
ax.text(0.5, 0.72, "“Woe to those who give short measure”", ha="center", fontsize=12, style="italic", color="#444")
panels = [("Indonesia (Kemenag)", q["terjemah_id"], "curang → moral; measuring gloss kept", "#1b7837", None),
          ("Malaysia (Basmeih)",   q["terjemah_ms"], "curang → moral; gloss kept",           "#1b7837", None),
          ("Brunei (KHEU)",        q["terjemah_bn"], "menipu (deceive); gloss kept",          "#2166ac", None),
          ("Thailand (Rowwad)",    q["terjemah_th"], "‘cause deficiency’ → technical",        "#b2182b", TH_FONT),
          ("Philippines (Tagalog)",q["terjemah_tl"], "petty theft; NO gloss; ‘grief’ not ‘woe’","#b2182b", None)]
y = 0.60
for name, txt, note, col, fnt in panels:
    ax.text(0.03, y, name, fontsize=11, weight="bold", color=col)
    t = txt if len(txt) < 92 else txt[:90] + "…"
    kw = {"fontproperties": fnt} if fnt else {}
    ax.text(0.03, y-0.045, t, fontsize=10, **kw)
    ax.text(0.03, y-0.083, "→ " + note, fontsize=9, style="italic", color=col)
    y -= 0.125
fig.savefig(os.path.join(FIG, "fig12_q83_closereading.png"), dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)

print("DONE: fig10_tsne_semantic_map.png, fig11_clustermap.png, fig12_q83_closereading.png")
print("Arabic font:", AR.get_name() if AR else "NOT FOUND")
