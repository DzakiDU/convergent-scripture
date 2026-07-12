#!/usr/bin/env Rscript
# =====================================================================
# 07_wordcloud.R  — Distinctive-vocabulary word clouds per edition
# Analogue of Lange et al. parsimonious word clouds. Focus on the
# Malay-family trio (Indonesia, Malaysia, Brunei): same language, so
# distinctive words reveal INSTITUTIONAL word choice (e.g. menipu vs curang).
# Distinctiveness = tf-idf across the three editions.
# =====================================================================
suppressPackageStartupMessages({
  library(readr); library(dplyr); library(tidyr); library(tidytext)
  library(stringr); library(ggplot2); library(ggwordcloud)
})
root <- if (nzchar(Sys.getenv("PROJ_ROOT"))) Sys.getenv("PROJ_ROOT") else getwd()
csvp   <- file.path(root, "data", "economic_verses_aligned.csv")
figdir <- file.path(root, "data", "out", "figs")
tabdir <- file.path(root, "data", "out", "tables"); dir.create(tabdir, showWarnings = FALSE, recursive = TRUE)

corpus <- read_csv(csvp, show_col_types = FALSE)
ed <- c(terjemah_id = "Indonesia (Kemenag)", terjemah_ms = "Malaysia (Basmeih)",
        terjemah_bn = "Brunei (KHEU)")   # Malay-family trio

# Indonesian/Malay function-word stoplist (compact)
stop_ms <- c("yang","dan","itu","ini","di","ke","dari","untuk","pada","dengan","atau",
  "mereka","kamu","akan","tidak","tak","adalah","telah","kepada","oleh","bagi","maka",
  "jika","agar","serta","kerana","karena","dia","ia","kami","kita","aku","engkau",
  "hendaklah","sesungguhnya","maha","allah","tuhan","apa","apabila","iaitu","yaitu",
  "orang","dalam","para","antara","sebagai","juga","lagi","pun","supaya","kecuali",
  "kerananya","nya","mu","ku","se","para","kan","lah","wahai","hai","dsb","yakni",
  "sekalian","antaramu","antara","seperti","bahawa","bahwa","adapun","segala","semua")

# Distinctive terms via a PARSIMONIOUS language model (Hiemstra et al. 2004),
# the same instrument class as Lange et al.'s weighwords word clouds. Weights are
# computed in scripts/12_parsimonious_wordcloud.py; here we only draw them.
pars <- read_csv(file.path(tabdir, "tab4_distinctive_terms.csv"), show_col_types = FALSE)

set.seed(3)
p <- ggplot(pars, aes(label = word, size = weight, color = Edition)) +
  geom_text_wordcloud_area(area_corr_power = 1) +
  scale_size_area(max_size = 14) +
  facet_wrap(~ Edition) +
  theme_minimal(base_size = 12) +
  theme(strip.text = element_text(size = 12), panel.grid = element_blank()) +
  labs(title = "Distinctive vocabulary per Malay-family edition (parsimonious language model)",
       subtitle = "same language, different state authority: word choice reveals institutional divergence")
ggsave(file.path(figdir, "fig7_wordcloud_malay.png"), p, width = 10, height = 4.2, dpi = 200, bg = "white")

cat("DONE. fig7_wordcloud_malay.png + tab4_distinctive_terms.csv\n")

# =====================================================================
# fig8 — THEMATIC muamalat word cloud (frequency-based, content words)
# Shows what the corpus is ABOUT (riba, harta, timbangan, waris ...).
# Uses the Indonesian (Kemenag) edition as canonical to avoid double-
# counting Malay/Indonesian spelling variants.
# =====================================================================
stop_extra <- c("tiap","kalau","satu","sungguh","sentiasa","perkara","mengenai","sesiapa",
  "bani","duanya","tidaklah","keras","dirimu","diantara","penuhilah","dipenuhi",
  "beruntung","bagimu","dimu","kamupun","sebagian","sebahagian","ialah","adapun",
  "hendaknya","betul","betulkanlah","kalalah","begitu","antaramu","kepadamu","darimu",
  "mahu","mahupun","boleh","dapat","sahaja","hanya","tetapi","namun","demikian","yakni")

tok_id <- corpus |>
  select(surah_ayat, terjemah_id) |>
  unnest_tokens(word, terjemah_id) |>
  filter(!str_detect(word, "^[0-9]+$"), str_length(word) > 2,
         !word %in% c(stop_ms, stop_extra)) |>
  count(word, sort = TRUE) |>
  slice_max(n, n = 55, with_ties = FALSE)
write_csv(tok_id, file.path(tabdir, "tab5_muamalat_terms.csv"))

set.seed(5)
p8 <- ggplot(tok_id, aes(label = word, size = n, color = n)) +
  geom_text_wordcloud_area(area_corr_power = 1) +
  scale_size_area(max_size = 22) +
  scale_color_viridis_c(option = "mako", direction = -1, end = 0.85) +
  theme_minimal(base_size = 12) +
  theme(panel.grid = element_blank()) +
  labs(title = "Thematic vocabulary of the muamalat corpus (frequency)",
       subtitle = "Indonesian (Kemenag) edition; function words removed")
ggsave(file.path(figdir, "fig8_wordcloud_themes.png"), p8, width = 8.5, height = 5.5, dpi = 200, bg = "white")

cat("DONE. fig8_wordcloud_themes.png + tab5_muamalat_terms.csv\n")
print(head(tok_id, 20))
