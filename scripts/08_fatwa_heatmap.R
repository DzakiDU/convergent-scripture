#!/usr/bin/env Rscript
# =====================================================================
# 08_fatwa_heatmap.R  — Fatwa strictness heatmap (country x issue)
# Companion to fig1 (translation similarity). Shows the DIVERGENCE that
# the translation layer hides: same scripture, different fatwa postures.
# strictness 1 = most permissive ... 5 = strictest.
# =====================================================================
suppressPackageStartupMessages({
  library(readr); library(dplyr); library(ggplot2); library(forcats)
})
root <- if (nzchar(Sys.getenv("PROJ_ROOT"))) Sys.getenv("PROJ_ROOT") else getwd()
csvp   <- file.path(root, "data", "fatwa_comparison.csv")
figdir <- file.path(root, "data", "out", "figs"); dir.create(figdir, showWarnings = FALSE, recursive = TRUE)

f <- read_csv(csvp, show_col_types = FALSE) |>
  filter(country %in% c("Indonesia", "Malaysia", "Singapore", "Brunei")) |>
  mutate(issue = factor(issue,
           levels = c("Bank interest", "Insurance/takaful", "Crypto", "Tawarruq"),
           labels = c("Bank\ninterest", "Insurance", "Crypto", "Tawarruq")),
         flag = dplyr::case_when(evidence_tier == "inference" ~ "*",
                                 evidence_tier == "advisory"  ~ "**",
                                 TRUE ~ ""))

# order countries by mean strictness (most permissive at bottom)
ord <- f |> group_by(country) |> summarise(m = mean(strictness_1to5)) |> arrange(m) |> pull(country)
f <- f |> mutate(country = factor(country, levels = ord))

p <- ggplot(f, aes(issue, country, fill = strictness_1to5)) +
  geom_tile(color = "white", linewidth = 1.2) +
  geom_text(aes(label = paste0(strictness_1to5, flag)),
            color = ifelse(f$strictness_1to5 >= 3, "white", "grey15"), size = 5) +
  scale_fill_viridis_c(option = "rocket", direction = -1, limits = c(1, 5),
                       name = "strictness", breaks = 1:5) +
  labs(title = "Fatwa strictness on muamalat issues, by state",
       subtitle = "strictness 1 (permissive) to 5 (strict).   * inference,  ** regulatory advisory (not a fatwa)",
       x = NULL, y = NULL,
       caption = "Benchmark: OIC Fiqh Academy (2009) ruled organized tawarruq prohibited (5).") +
  coord_fixed() +
  theme_minimal(base_size = 12) +
  theme(panel.grid = element_blank(),
        plot.subtitle = element_text(color = "grey35", size = 9.5),
        plot.caption = element_text(color = "grey45", size = 8.5, hjust = 0),
        axis.text = element_text(size = 11))
ggsave(file.path(figdir, "fig9_fatwa_strictness.png"), p, width = 7.6, height = 4.6, dpi = 200, bg = "white")
cat("DONE. fig9_fatwa_strictness.png | country order (permissive->strict):", paste(ord, collapse=" < "), "\n")
