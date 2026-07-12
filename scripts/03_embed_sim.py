#!/usr/bin/env python3
"""Proof-of-concept pipeline (pengganti M2 Lange): kemiripan rendering lintas-edisi.

Jangkar = ayat Arab yang sama; kita ukur seberapa MIRIP/BERBEDA terjemahan
muamalah tiap edisi ASEAN via multilingual embeddings (LaBSE).

Output:
  data/out/lang_similarity_matrix.csv  -> matriks kemiripan antar-bahasa
  data/out/domain_divergence.csv       -> domain muamalah paling divergen
  data/out/most_divergent_verses.csv   -> ayat dgn kesepakatan lintas-edisi terendah
"""
import csv, os, itertools
import numpy as np
from sentence_transformers import SentenceTransformer

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV  = os.path.join(HERE, "data", "economic_verses_aligned.csv")
OUT  = os.path.join(HERE, "data", "out"); os.makedirs(OUT, exist_ok=True)

LANGS = ["id", "ms", "th", "tl", "bn"]     # Indonesia, Malaysia(Basmeih), Thai, Tagalog
rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
print(f"Ayat: {len(rows)} | Bahasa: {LANGS}")

print("Muat model LaBSE (unduh sekali ~1.8GB)...")
model = SentenceTransformer("sentence-transformers/LaBSE")

# embed tiap bahasa; simpan matriks [n_ayat, dim] per bahasa
emb = {}
for lg in LANGS:
    texts = [r[f"terjemah_{lg}"] for r in rows]
    emb[lg] = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

def cos(a, b): return float(np.dot(a, b))

# --- 1) Matriks kemiripan antar-bahasa (rata-rata cosine rendering ayat yg sama) ---
pair_sim = {}
for a, b in itertools.combinations(LANGS, 2):
    sims = [cos(emb[a][i], emb[b][i]) for i in range(len(rows))]
    pair_sim[(a, b)] = float(np.mean(sims))

with open(os.path.join(OUT, "lang_similarity_matrix.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow([""] + LANGS)
    for a in LANGS:
        row = [a]
        for b in LANGS:
            if a == b: row.append(1.0)
            else: row.append(round(pair_sim.get((a, b) if (a, b) in pair_sim else (b, a)), 4))
        w.writerow(row)
print("\nKemiripan antar-edisi (mean cosine):")
for (a, b), v in sorted(pair_sim.items(), key=lambda x: -x[1]):
    print(f"  {a}-{b}: {v:.3f}")

# --- 2) Divergensi per domain muamalah (1 - mean pairwise cosine) ---
from collections import defaultdict
dom_idx = defaultdict(list)
for i, r in enumerate(rows): dom_idx[r["tema"]].append(i)

dom_div = {}
for dom, idxs in dom_idx.items():
    vals = []
    for i in idxs:
        for a, b in itertools.combinations(LANGS, 2):
            vals.append(cos(emb[a][i], emb[b][i]))
    dom_div[dom] = 1 - float(np.mean(vals))
with open(os.path.join(OUT, "domain_divergence.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["domain", "divergence", "n_ayat"])
    for dom, d in sorted(dom_div.items(), key=lambda x: -x[1]):
        w.writerow([dom, round(d, 4), len(dom_idx[dom])])
print("\nDomain muamalah paling DIVERGEN antar-edisi (makin tinggi=makin beda tafsir):")
for dom, d in sorted(dom_div.items(), key=lambda x: -x[1])[:6]:
    print(f"  {d:.3f}  {dom}")

# --- 3) Ayat paling divergen (kandidat close reading) ---
verse_div = []
for i, r in enumerate(rows):
    vals = [cos(emb[a][i], emb[b][i]) for a, b in itertools.combinations(LANGS, 2)]
    verse_div.append((r["surah_ayat"], r["tema"], 1 - float(np.mean(vals))))
verse_div.sort(key=lambda x: -x[2])
with open(os.path.join(OUT, "most_divergent_verses.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["surah_ayat", "tema", "divergence"])
    for sa, tm, d in verse_div: w.writerow([sa, tm, round(d, 4)])
print("\nAyat paling divergen (top-8, layak close reading):")
for sa, tm, d in verse_div[:8]:
    print(f"  {d:.3f}  {sa} [{tm}]")

# --- 4) Long form: cosine per-ayat per-pasangan (untuk bootstrap/uji di R) ---
with open(os.path.join(OUT, "pairwise_long.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["surah_ayat", "tema", "pair", "cosine"])
    for i, r in enumerate(rows):
        for a, b in itertools.combinations(LANGS, 2):
            w.writerow([r["surah_ayat"], r["tema"], f"{a}-{b}",
                        round(cos(emb[a][i], emb[b][i]), 4)])

# per-ayat divergensi (untuk uji beda antar-domain di R)
with open(os.path.join(OUT, "verse_divergence.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["surah_ayat", "tema", "divergence"])
    for sa, tm, d in verse_div: w.writerow([sa, tm, round(d, 4)])

# --- 5) Jaringan semantik antar-ayat (centroid lintas-edisi) untuk ggraph ---
div_map = {sa: d for sa, tm, d in verse_div}
cent = []
for i in range(len(rows)):
    v = np.mean([emb[lg][i] for lg in LANGS], axis=0)
    cent.append(v / (np.linalg.norm(v) + 1e-9))
with open(os.path.join(OUT, "verse_network_nodes.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["id", "surah_ayat", "domain", "divergence"])
    for i, r in enumerate(rows):
        w.writerow([i, r["surah_ayat"], r["tema"], div_map[r["surah_ayat"]]])
with open(os.path.join(OUT, "verse_network_edges.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["from", "to", "weight"])
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            c = cos(cent[i], cent[j])
            if c >= 0.45:
                w.writerow([i, j, round(c, 4)])

print(f"\nSemua output tersimpan di {OUT}/")
