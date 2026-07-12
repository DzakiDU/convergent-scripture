#!/usr/bin/env Rscript
# =====================================================================
# 05_stats.R  — Uji statistik atas hasil kemiripan/divergensi (RStudio)
# Membaca data/out/pairwise_long.csv & verse_divergence.csv
# Menghasilkan: bootstrap 95% CI per pasangan edisi (+ forest plot),
# uji within- vs cross-family (Wilcoxon), uji beda antar-domain (Kruskal).
# =====================================================================
suppressPackageStartupMessages({
  library(readr); library(dplyr); library(tidyr); library(ggplot2)
})
root   <- if (nzchar(Sys.getenv("PROJ_ROOT"))) Sys.getenv("PROJ_ROOT") else getwd()
outdir <- file.path(root, "data", "out")
figdir <- file.path(outdir, "figs"); dir.create(figdir, showWarnings = FALSE, recursive = TRUE)
tabdir <- file.path(outdir, "tables"); dir.create(tabdir, showWarnings = FALSE, recursive = TRUE)

pair_lab <- c("id-ms"="Indonesia–Malaysia", "id-th"="Indonesia–Thailand",
              "id-tl"="Indonesia–Philippines", "id-bn"="Indonesia–Brunei",
              "ms-th"="Malaysia–Thailand", "ms-tl"="Malaysia–Philippines",
              "ms-bn"="Malaysia–Brunei", "th-tl"="Thailand–Philippines",
              "th-bn"="Thailand–Brunei", "tl-bn"="Philippines–Brunei")
malay_pairs <- c("id-ms", "id-bn", "ms-bn")   # semua serumpun Melayu (ID/MS/BN)

pw <- read_csv(file.path(outdir, "pairwise_long.csv"), show_col_types = FALSE)

# ---- 1) Bootstrap 95% CI mean cosine per pasangan edisi ----
set.seed(42)
bootci <- function(x, R = 10000) {
  m <- replicate(R, mean(sample(x, replace = TRUE)))
  c(mean = mean(x), lo = unname(quantile(m, .025)), hi = unname(quantile(m, .975)))
}
ci <- pw |> group_by(pair) |>
  group_modify(~ as.data.frame(t(bootci(.x$cosine)))) |> ungroup() |>
  mutate(label = pair_lab[pair],
         family = ifelse(pair %in% malay_pairs, "Malay family", "Cross-family"))
write_csv(ci, file.path(tabdir, "tab3_pair_bootstrap_ci.csv"))
cat("\n== Bootstrap 95% CI mean cosine per pasangan ==\n")
print(ci |> transmute(label, mean = round(mean,3), CI = sprintf("[%.3f, %.3f]", lo, hi)), n = 6)

pfor <- ggplot(ci, aes(mean, reorder(label, mean), color = family)) +
  geom_errorbarh(aes(xmin = lo, xmax = hi), height = .22, linewidth = .8) +
  geom_point(size = 3) +
  geom_text(aes(label = sprintf("%.2f", mean)), vjust = -1, size = 3.2, show.legend = FALSE) +
  scale_color_manual(values = c("Malay family" = "#1f6f78", "Cross-family" = "#b8860b"), name = NULL) +
  labs(title = "Cross-edition similarity with 95% bootstrap CI",
       subtitle = "n = 105 muamalat verses; LaBSE cosine per verse", x = "mean cosine", y = NULL) +
  theme_minimal(base_size = 12) +
  theme(panel.grid.minor = element_blank(), legend.position = "top",
        plot.subtitle = element_text(color = "grey35", size = 10))
ggsave(file.path(figdir, "fig5_pair_ci_forest.png"), pfor, width = 7.5, height = 4.6, dpi = 200)

# ---- 2) Within-family (id-ms) vs cross-family, uji Wilcoxon berpasangan ----
wide <- pw |> pivot_wider(names_from = pair, values_from = cosine, id_cols = surah_ayat)
cross_pairs <- setdiff(names(pair_lab), malay_pairs)
within <- rowMeans(wide[, malay_pairs])
cross  <- rowMeans(wide[, cross_pairs])
wt <- wilcox.test(within, cross, paired = TRUE, alternative = "greater")
cat(sprintf("\n== Institutional pair Malaysia–Brunei (serumpun, beda negara): mean cosine = %.3f ==\n",
            mean(wide[["ms-bn"]])))
cat("\n== Within-family (ID/MS/BN Melayu) vs rata-rata lintas-rumpun ==\n")
cat(sprintf("  median within = %.3f | median cross = %.3f\n", median(within), median(cross)))
cat(sprintf("  Wilcoxon berpasangan (within > cross): V = %.0f, p = %.2e\n", wt$statistic, wt$p.value))

# ---- 3) Beda divergensi antar-domain muamalah (Kruskal-Wallis) ----
vd <- read_csv(file.path(outdir, "verse_divergence.csv"), show_col_types = FALSE)
vd_big <- vd |> group_by(tema) |> filter(n() >= 3) |> ungroup()   # domain dgn n>=3 saja
kw <- kruskal.test(divergence ~ tema, data = vd_big)
cat("\n== Beda divergensi antar-domain (n>=3 per domain) ==\n")
cat(sprintf("  Kruskal-Wallis: chi2 = %.2f, df = %d, p = %.3f\n", kw$statistic, kw$parameter, kw$p.value))
cat("  (catatan: n per domain kecil; uji ini indikatif, bukan konfirmatif)\n")

sink(file.path(tabdir, "stats_summary.txt"))
cat("Ringkasan uji statistik POC\n===========================\n")
print(ci); cat("\nWilcoxon within>cross: V=", wt$statistic, " p=", wt$p.value, "\n")
cat("Kruskal antar-domain: chi2=", kw$statistic, " df=", kw$parameter, " p=", kw$p.value, "\n")
sink()
cat("\nSELESAI. Figur -> fig5_pair_ci_forest.png ; ringkasan -> tables/stats_summary.txt\n")
