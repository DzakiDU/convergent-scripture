#!/usr/bin/env Rscript
# Install the R packages used by the figure/stat/table scripts (04-08).
pkgs <- c(
  "ggplot2", "dplyr", "tidyr", "readr", "stringr", "forcats",
  "viridisLite", "scales", "kableExtra",   # figures & tables
  "tidytext", "ggwordcloud",               # word clouds (07)
  "igraph", "ggraph"                        # similarity network (06)
)
miss <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]
if (length(miss)) {
  message("Installing: ", paste(miss, collapse = ", "))
  install.packages(miss, repos = "https://cloud.r-project.org")
} else {
  message("All R packages already installed.")
}
