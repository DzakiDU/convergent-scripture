# Convergent Scripture, Divergent Rulings

**Text-mining the muʿāmalāt verses across five Southeast Asian Qur'an editions.**

This repository reproduces the analysis behind the paper *Convergent Scripture,
Divergent Rulings: How Southeast Asian States Translate and Rule on the Economic
Qur'an* (submitted to *Studia Islamika*). It transposes the text-mining method of
Lange, van Kuppevelt & van der Zwaan (2021), *Text Mining Islamic Law*, from a
mono-lingual, diachronic Arabic corpus to a **multilingual, synchronic** corpus of
national Qur'an translations.

**Core finding — the two layers decouple.** *Translation* is a layer of
**convergence**: cross-edition similarity is governed by language family, and the
Malay editions of Malaysia and Brunei are the most similar pair (mean cosine 0.92).
*Fatwa* is the layer of **divergence**: on bank interest, insurance, cryptocurrency,
and tawarruq the same states run from most to least permissive as Malaysia,
Singapore, Brunei, Indonesia — an ordering their translations do **not** predict.

## Method: Lange et al. → this study

| Lange et al. (2021) | This study |
|---------------------|------------|
| Text-reuse network (detects shared citations) | **Cross-edition semantic similarity** (LaBSE cosine) — reuse is trivial when all editions render one Arabic source |
| word2vec trained on the corpus (mono-lingual) | **LaBSE** language-agnostic sentence embeddings (5 languages in one space) |
| Parsimonious word clouds (`weighwords`) | **Parsimonious language model** (Hiemstra et al. 2004), same instrument, on the Malay-family trio |
| Frequency analysis (BlackLab) | Frequency word cloud of the muʿāmalāt corpus |
| LDA topic modeling | Per-domain divergence (105 verses is too sparse for stable LDA) |

## Repository layout

```
data/
  economic_verses_aligned.csv     # the corpus: 105 verses x 5 editions (+ Arabic, footnotes)
  fatwa_comparison.csv            # fatwa strictness coding, 4 issues x 4 states
  out/                            # derived data (committed, so the notebook runs offline)
    embeddings.npy                #   LaBSE vectors, 525 x 768  ([id,ms,th,tl,bn] x 105)
    lang_similarity_matrix.csv    #   5x5 mean-cosine matrix
    domain_divergence.csv, pairwise_long.csv, verse_divergence.csv, ...
    figs/                         #   all figures (PNG)
    tables/                       #   publication tables (CSV/HTML/LaTeX)
scripts/                          # the pipeline (see below)
notebooks/
  reproduce_analysis.ipynb        # self-contained showcase: matrix, divergence, stats, two-layer
manuscript/                       # the paper (gitignored by default)
requirements.txt                  # light stack (reproduce from cached data)
requirements-embeddings.txt       # heavy stack (recompute LaBSE from scratch)
install.R                         # R packages for figures/tables
run_all.sh                        # regenerate everything end to end
```

## Quick start (5 minutes, no GPU, no model download)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook notebooks/reproduce_analysis.ipynb
```

The notebook loads the cached `embeddings.npy`, recomputes the similarity matrix
(it asserts it matches the reported values), reproduces the domain-divergence chart,
re-runs the Wilcoxon and Kruskal–Wallis tests in Python, and plots the two-layer
decoupling — all from committed data, no network access required.

## Full pipeline

The pipeline is a Python → CSV → R hand-off. Run it end to end with:

```bash
bash run_all.sh
```

or step by step:

| Step | Script | Output |
|------|--------|--------|
| 1 | `01_fetch_corpus.py` | rebuilds `economic_verses_aligned.csv` (needs network) |
| 2 | `03_embed_sim.py` | LaBSE embeddings + similarity/divergence CSVs (needs heavy stack) |
| 3 | `04_visualize.R` | fig1–4, publication tables |
| 4 | `05_stats.R` | bootstrap CI + Wilcoxon + Kruskal (fig5) |
| 5 | `06_network.R` | fig6 verse similarity network |
| 6 | `12_parsimonious_wordcloud.py` → `07_wordcloud.R` | fig7 (parsimonious) + fig8 (thematic) |
| 7 | `08_fatwa_heatmap.R` | fig9 fatwa-strictness heatmap |
| 8 | `10_python_figures.py`, `11_more_figures.py` | supplementary figures (t-SNE, choropleth, …) |
| 9 | `09_build_docx.py` | assembles the manuscript (optional) |

## Data

See **[DATA_SOURCES.md](DATA_SOURCES.md)** for the provenance of each edition and an
important caveat: Indonesia/Malaysia/Brunei are state-authorised editions, whereas
Thailand and the Philippines use the open **Rowwad** editions (no clean state text
is available). Translation strings remain the property of their authorities and are
included only as verse-level scholarly excerpts.

## Citation

If you use this code or corpus, please cite the paper (see `CITATION.cff`) and the
method it builds on:

> Lange, Christian, Dafne van Kuppevelt, and Janneke van der Zwaan. 2021. "Text
> Mining Islamic Law." *Islamic Law and Society* 28: 234–281.

## License

Code: MIT (`LICENSE`). Translation data: property of the respective authorities,
verse-level excerpts only. See the note in `LICENSE` and `DATA_SOURCES.md`.
