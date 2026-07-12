#!/usr/bin/env Rscript
# =====================================================================
# 06_network.R  — Semantic similarity network of muamalat verses
# Analogue of Lange et al. Fig 2.1-2.3, transposed: nodes = verses,
# edges = high cross-edition-centroid cosine, colour = muamalat domain,
# size = divergence. Force-directed (Fruchterman-Reingold).
# =====================================================================
suppressPackageStartupMessages({
  library(readr); library(dplyr); library(igraph); library(ggraph); library(ggplot2)
})
root <- if (nzchar(Sys.getenv("PROJ_ROOT"))) Sys.getenv("PROJ_ROOT") else getwd()
outdir <- file.path(root, "data", "out"); figdir <- file.path(outdir, "figs")

domain_en <- c(
  "riba"="Riba (usury)", "mizan-timbangan-adil"="Measures & scales",
  "zakat-infaq"="Zakat & alms", "infaq-etika"="Spending ethics",
  "harta-anak-yatim"="Orphans' property", "warisan-faraid"="Inheritance",
  "uqud-akad-janji"="Contracts & oaths", "gharar-maysir-judi"="Gharar & gambling",
  "bay-jualbeli"="Sale & trade", "amanah-trust"="Trust (amanah)",
  "penimbunan-kanz"="Hoarding", "rezeki-kerja-halal"="Lawful earning",
  "wasiat"="Bequest", "harta-batil-suap"="Unlawful gain",
  "distribusi-kekayaan"="Wealth distribution")

nodes <- read_csv(file.path(outdir, "verse_network_nodes.csv"), show_col_types = FALSE) |>
  mutate(Domain = domain_en[domain])
edges <- read_csv(file.path(outdir, "verse_network_edges.csv"), show_col_types = FALSE) |>
  filter(weight >= 0.62)            # display threshold for legibility

g <- graph_from_data_frame(edges, vertices = nodes, directed = FALSE)
set.seed(7)
lab <- nodes |> slice_max(divergence, n = 10) |> pull(surah_ayat)

p <- ggraph(g, layout = "fr") +
  geom_edge_link(aes(alpha = weight), edge_colour = "grey70", show.legend = FALSE) +
  scale_edge_alpha(range = c(0.05, 0.5)) +
  geom_node_point(aes(color = Domain, size = divergence)) +
  geom_node_text(aes(label = ifelse(surah_ayat %in% lab, paste0("Q", surah_ayat), "")),
                 repel = TRUE, size = 3, colour = "grey15") +
  scale_size(range = c(2, 8), name = "divergence") +
  scale_color_manual(values = scales::hue_pal()(length(unique(nodes$Domain))), name = "Muamalat domain") +
  labs(title = "Semantic network of muamalat verses across Southeast Asian editions",
       subtitle = "nodes = verses; edges = high cross-edition-centroid similarity; labels = most divergent verses") +
  theme_void(base_size = 12) +
  theme(plot.title = element_text(size = 13, margin = margin(b = 2)),
        plot.subtitle = element_text(colour = "grey35", size = 10, margin = margin(b = 8)),
        legend.text = element_text(size = 9), legend.key.size = unit(0.9, "lines"),
        plot.margin = margin(10, 10, 10, 10))
ggsave(file.path(figdir, "fig6_verse_network.png"), p, width = 9.8, height = 7.2, dpi = 200, bg = "white")
cat("DONE. fig6_verse_network.png | nodes:", vcount(g), " edges shown:", ecount(g), "\n")
