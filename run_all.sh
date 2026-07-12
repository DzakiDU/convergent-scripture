#!/usr/bin/env bash
# Regenerate the analysis end to end. From the repo root: bash run_all.sh
# Steps needing the heavy stack (01 network, 03/10/11 embeddings) are guarded so a
# light-stack user can still rebuild every figure from the cached embeddings.
set -euo pipefail
export PROJ_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJ_ROOT"

have_py () { python3 -c "import $1" >/dev/null 2>&1; }

echo "== [1/8] corpus =="
if have_py urllib.request && [ "${REFETCH:-0}" = "1" ]; then
  python3 scripts/01_fetch_corpus.py
else
  echo "   skip 01_fetch_corpus (set REFETCH=1 to re-download from QuranEnc/Quran.com)"
fi

echo "== [2/8] embeddings + similarity =="
if have_py sentence_transformers; then
  python3 scripts/03_embed_sim.py
else
  echo "   skip 03_embed_sim (heavy stack absent); using cached data/out/embeddings.npy"
fi

echo "== [3/8] figures 1-4 + tables =="; Rscript scripts/04_visualize.R
echo "== [4/8] stats + fig5 =========="; Rscript scripts/05_stats.R
echo "== [5/8] network fig6 =========="; Rscript scripts/06_network.R
echo "== [6/8] word clouds (parsimonious fig7 + thematic fig8) =="
python3 scripts/12_parsimonious_wordcloud.py
Rscript scripts/07_wordcloud.R
echo "== [7/8] fatwa heatmap fig9 ===="; Rscript scripts/08_fatwa_heatmap.R

echo "== [8/8] supplementary python figures =="
if have_py sentence_transformers && have_py sklearn; then
  python3 scripts/10_python_figures.py
  python3 scripts/11_more_figures.py
else
  echo "   skip 10/11 (heavy stack absent)"
fi

echo "DONE. Figures -> data/out/figs ; tables -> data/out/tables"
