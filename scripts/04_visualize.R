#!/usr/bin/env Rscript
# =====================================================================
# 04_visualize.R  — Figures & publication tables (ENGLISH, for RStudio)
# Reads Python output (data/out/*.csv); writes figs + LaTeX/HTML/CSV tables.
# Hybrid workflow: Python -> CSV ; R -> journal figures & tables.
# =====================================================================
suppressPackageStartupMessages({
  need <- c("ggplot2","tidyr","dplyr","readr","viridisLite","scales","kableExtra")
  miss <- need[!vapply(need, requireNamespace, logical(1), quietly = TRUE)]
  if (length(miss)) stop("Missing R packages: ", paste(miss, collapse=", "))
  library(ggplot2); library(tidyr); library(dplyr); library(readr); library(kableExtra)
})
root   <- if (nzchar(Sys.getenv("PROJ_ROOT"))) Sys.getenv("PROJ_ROOT") else getwd()
outdir <- file.path(root, "data", "out")
figdir <- file.path(outdir, "figs"); dir.create(figdir, showWarnings = FALSE, recursive = TRUE)
tabdir <- file.path(outdir, "tables"); dir.create(tabdir, showWarnings = FALSE, recursive = TRUE)

edition <- c(id = "Indonesia (Kemenag)", ms = "Malaysia (Basmeih)",
             th = "Thailand (Rowwad)",  tl = "Philippines (Tagalog)",
             bn = "Brunei (KHEU)")
domain_en <- c(
  "riba"="Riba (usury)", "mizan-timbangan-adil"="Measures & scales",
  "zakat-infaq"="Zakat & alms", "infaq-etika"="Spending ethics",
  "harta-anak-yatim"="Orphans' property", "warisan-faraid"="Inheritance",
  "uqud-akad-janji"="Contracts & oaths", "gharar-maysir-judi"="Gharar & gambling",
  "bay-jualbeli"="Sale & trade", "amanah-trust"="Trust (amanah)",
  "penimbunan-kanz"="Hoarding", "rezeki-kerja-halal"="Lawful earning",
  "wasiat"="Bequest", "harta-batil-suap"="Unlawful gain",
  "distribusi-kekayaan"="Wealth distribution",
  "ijarah"="Leasing (ijara)", "syirkah-mudharabah"="Partnership & mudaraba",
  "produksi"="Production", "qard-utang"="Lending & debt",
  "harta-fitnah"="Wealth as trial")

theme_pub <- theme_minimal(base_size = 12) +
  theme(panel.grid.minor = element_blank(),
        plot.title = element_text(face = "plain", size = 13),
        plot.subtitle = element_text(color = "grey35", size = 10),
        axis.title = element_text(size = 11))

# ---- 1) Heatmap of cross-edition similarity ----
M <- as.matrix(read.csv(file.path(outdir, "lang_similarity_matrix.csv"),
                        row.names = 1, check.names = FALSE))
long <- as.data.frame(as.table(M)) |> setNames(c("A","B","sim")) |>
  mutate(A = edition[as.character(A)], B = edition[as.character(B)])
p1 <- ggplot(long, aes(B, A, fill = sim)) +
  geom_tile(color = "white", linewidth = 1) +
  geom_text(aes(label = sprintf("%.2f", sim)),
            color = ifelse(long$sim > 0.9, "white", "grey10"), size = 4) +
  scale_fill_viridis_c(option = "mako", direction = -1, limits = c(0.65, 1), name = "cosine") +
  labs(title = "Cross-edition similarity of muamalat renderings",
       subtitle = "LaBSE mean cosine; darker = more similar", x = NULL, y = NULL) +
  coord_fixed() + theme_pub + theme(axis.text.x = element_text(angle = 25, hjust = 1))
ggsave(file.path(figdir, "fig1_similarity_heatmap.png"), p1, width = 7.4, height = 6, dpi = 200)

# ---- 2) Dendrogram of editions ----
hc <- hclust(as.dist(1 - M), method = "average")
png(file.path(figdir, "fig2_edition_dendrogram.png"), width = 1500, height = 950, res = 200)
op <- par(mar = c(3,4,3,1))
plot(hc, labels = edition[hc$labels],
     main = "Clustering of editions by muamalat rendering similarity",
     xlab = "", sub = "", ylab = "distance (1 - cosine)", cex = 0.9)
par(op); dev.off()

# ---- 3) Divergence per muamalat domain ----
dom <- read_csv(file.path(outdir, "domain_divergence.csv"), show_col_types = FALSE) |>
  mutate(domain_lab = domain_en[domain])
p3 <- dom |> filter(n_ayat >= 3) |> mutate(domain_lab = reorder(domain_lab, divergence)) |>
  ggplot(aes(divergence, domain_lab)) +
  geom_col(fill = viridisLite::viridis(1, begin = .35), width = .72) +
  geom_text(aes(label = sprintf("%.2f  (n=%d)", divergence, n_ayat)),
            hjust = -0.08, size = 3.3, color = "grey25") +
  scale_x_continuous(expand = expansion(mult = c(0, 0.2))) +
  labs(title = "Which muamalat domains diverge most across editions",
       subtitle = "divergence = 1 - mean cross-edition cosine; only domains with n >= 3 verses",
       x = "divergence", y = NULL) + theme_pub
ggsave(file.path(figdir, "fig3_domain_divergence.png"), p3, width = 7.8, height = 5, dpi = 200)

# ---- 4) Most divergent verses (close-reading candidates) ----
ver <- read_csv(file.path(outdir, "most_divergent_verses.csv"), show_col_types = FALSE) |>
  slice_max(divergence, n = 12) |>
  mutate(lab = paste0("Q ", surah_ayat, "  [", domain_en[tema], "]"),
         lab = reorder(lab, divergence))
p4 <- ggplot(ver, aes(divergence, lab)) +
  geom_segment(aes(x = 0, xend = divergence, y = lab, yend = lab), color = "grey75") +
  geom_point(size = 3.2, color = viridisLite::viridis(1, begin = .5)) +
  geom_text(aes(label = sprintf("%.2f", divergence)), hjust = -0.4, size = 3.2, color = "grey25") +
  scale_x_continuous(expand = expansion(mult = c(0, 0.15))) +
  labs(title = "Most divergent muamalat verses (top 12)",
       subtitle = "candidates for close reading", x = "divergence", y = NULL) + theme_pub
ggsave(file.path(figdir, "fig4_divergent_verses.png"), p4, width = 7.8, height = 5, dpi = 200)

# ---- 5) Publication tables (LaTeX + HTML + CSV) ----
export_tbl <- function(k_latex, k_html, df, stem) {
  try(save_kable(k_latex, file.path(tabdir, paste0(stem, ".tex"))), silent = TRUE)
  try(writeLines(as.character(k_html), file.path(tabdir, paste0(stem, ".html"))), silent = TRUE)
  readr::write_csv(df, file.path(tabdir, paste0(stem, ".csv")))
}
Mtab <- M; dimnames(Mtab) <- list(edition[rownames(M)], edition[colnames(M)])
Mdf <- data.frame(Edition = rownames(Mtab), round(Mtab, 3), check.names = FALSE)
export_tbl(
  kbl(round(Mtab,3), format="latex", booktabs=TRUE,
      caption="Cross-edition similarity of muamalat renderings (LaBSE mean cosine).") |>
    kable_styling(latex_options="hold_position"),
  kbl(round(Mtab,3), format="html", caption="Cross-edition similarity (mean cosine)") |>
    kable_styling(full_width=FALSE),
  Mdf, "tab1_similarity")

domt <- dom |> arrange(desc(divergence)) |>
  transmute(Domain = domain_lab, Divergence = divergence, `n verses` = n_ayat)
export_tbl(
  kbl(domt, format="latex", booktabs=TRUE, digits=3,
      caption="Cross-edition divergence by muamalat domain.") |>
    kable_styling(latex_options="hold_position"),
  kbl(domt, format="html", digits=3, caption="Divergence by muamalat domain") |>
    kable_styling(full_width=FALSE),
  domt, "tab2_domain_divergence")

cat("\nDONE (English).  figs ->", figdir, "\n  tables ->", tabdir, "\n")
