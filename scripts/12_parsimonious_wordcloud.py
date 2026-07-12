#!/usr/bin/env python3
"""fig7 distinctive-vocabulary weights via a PARSIMONIOUS language model
(Hiemstra et al. 2004) — the SAME instrument Lange et al. (2021) use for their
word clouds (their weighwords package), applied here to the Malay-family trio
(Indonesia, Malaysia, Brunei). Replaces the tf-idf proxy.

The PyPI `weighwords` 0.2 is Python-2 code and will not run on modern NumPy/
Python, so we implement its exact EM directly. For a document D with term
frequencies tf(t,D), a fixed background model P(t|C) (pooled trio), and document
weight alpha (= weighwords' `w`), EM fits a parsimonious P(t|D):
    E:  e_t = tf(t,D) * alpha*P(t|D) / ( alpha*P(t|D) + (1-alpha)*P(t|C) )
    M:  P(t|D) = e_t / sum_t e_t
Small alpha -> more parsimonious: only strongly edition-specific terms survive.
Writes tables/tab4_distinctive_terms.csv; the R script (07) draws fig7 from it.
"""
import os, csv, re
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV  = os.path.join(ROOT, "data", "economic_verses_aligned.csv")
TAB  = os.path.join(ROOT, "data", "out", "tables"); os.makedirs(TAB, exist_ok=True)

ALPHA = 0.10   # weighwords `w`: weight of the document model in the mixture
TOPK  = 25

# Malay-family trio + display labels identical to the R script (facets must match)
ED = {"terjemah_id": "Indonesia (Kemenag)",
      "terjemah_ms": "Malaysia (Basmeih)",
      "terjemah_bn": "Brunei (KHEU)"}

# same stoplist as 07_wordcloud.R (stop_ms + stop_extra)
STOP = set("""yang dan itu ini di ke dari untuk pada dengan atau mereka kamu akan tidak tak
adalah telah kepada oleh bagi maka jika agar serta kerana karena dia ia kami kita aku engkau
hendaklah sesungguhnya maha allah tuhan apa apabila iaitu yaitu orang dalam para antara sebagai
juga lagi pun supaya kecuali kerananya nya mu ku se kan lah wahai hai dsb yakni sekalian antaramu
seperti bahawa bahwa adapun segala semua tiap kalau satu sungguh sentiasa perkara mengenai sesiapa
bani duanya tidaklah keras dirimu diantara penuhilah dipenuhi beruntung bagimu dimu kamupun sebagian
sebahagian ialah hendaknya betul betulkanlah kalalah begitu kepadamu darimu mahu mahupun boleh dapat
sahaja hanya tetapi namun demikian
daripada mana saja setelah sesudah kemudian sekiranya setengahnya menjadi siapa
sebelum ketika kerap selalu masing seseorang barangsiapa""".split())

rows = list(csv.DictReader(open(CSV, encoding="utf-8")))

def toks(text):
    # join intra-word apostrophes / ʿayn so "manfaʿat" -> "manfaat" (not "manfa"+"at")
    t = re.sub(r"[ʿʻʼ'’`ʿʼ]", "", (text or "").lower())
    return [w for w in re.findall(r"[a-z]+", t) if len(w) > 2 and w not in STOP]

docs = {lab: [w for r in rows for w in toks(r[col])] for col, lab in ED.items()}
labels = list(docs.keys())

# background model P(t|C): pooled collection frequencies over the trio
bg_counts = Counter()
for lab in labels:
    bg_counts.update(docs[lab])
bg_total = sum(bg_counts.values())
Pc = {t: c / bg_total for t, c in bg_counts.items()}

def parsimonious(doc_tokens, alpha=ALPHA, iters=100, eps=1e-8):
    tf = Counter(doc_tokens)
    terms = list(tf)
    total = sum(tf.values())
    Pd = {t: tf[t] / total for t in terms}          # init: maximum likelihood
    for _ in range(iters):
        e = {}
        for t in terms:
            num = alpha * Pd[t]
            e[t] = tf[t] * num / (num + (1 - alpha) * Pc.get(t, 1e-12))
        Z = sum(e.values()) or 1.0
        newPd = {t: e[t] / Z for t in terms}
        if max(abs(newPd[t] - Pd[t]) for t in terms) < eps:
            Pd = newPd; break
        Pd = newPd
    return sorted(Pd.items(), key=lambda x: -x[1])

out = []
print("=== top distinctive terms per edition (parsimonious LM, alpha=%.2f) ===" % ALPHA)
for lab in labels:
    top = parsimonious(docs[lab])[:TOPK]
    print(f"\n{lab}:\n  " + ", ".join(f"{t}({w:.3f})" for t, w in top[:12]))
    for t, w in top:
        out.append({"Edition": lab, "word": t, "weight": float(w)})

with open(os.path.join(TAB, "tab4_distinctive_terms.csv"), "w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=["Edition", "word", "weight"]); wr.writeheader()
    wr.writerows(out)
print(f"\nWROTE tables/tab4_distinctive_terms.csv  ({len(out)} rows)")
