#' Run a basic two-group differential expression analysis
#'
#' For each gene (row), compares expression between two groups using a
#' Welch two-sample t-test and computes a log2 fold change of group means.
#' P-values are adjusted for multiple testing with the Benjamini-Hochberg
#' procedure.
#'
#' This is a simplified workflow intended for teaching/demonstration: it
#' does not model count data with a negative binomial distribution the way
#' DESeq2 or edgeR do, and assumes `counts` has already been normalized
#' (e.g. with [normalize_counts()]) if that matters for your use case.
#'
#' @param counts A numeric matrix, genes x samples.
#' @param group A vector (factor, character, or numeric) of length
#'   `ncol(counts)` with exactly two distinct values, giving each sample's
#'   group membership.
#' @param pseudocount A small constant added before log2 fold-change
#'   calculation to avoid `log2(0)`. Default `1`.
#'
#' @return A data.frame with one row per gene (row names preserved as a
#'   `gene` column) and columns `log2fc`, `pvalue`, and `padj`, sorted by
#'   ascending `padj`.
#'
#' @examples
#' counts <- matrix(
#'   c(10, 12, 11, 100, 110, 105, 5, 6, 4, 5, 4, 6),
#'   nrow = 2, byrow = TRUE,
#'   dimnames = list(c("gene1", "gene2"), paste0("sample", 1:6))
#' )
#' group <- c("control", "control", "control", "treated", "treated", "treated")
#' run_deg(counts, group)
#'
#' @export
run_deg <- function(counts, group, pseudocount = 1) {
  if (!is.matrix(counts) || !is.numeric(counts)) {
    stop("`counts` must be a numeric matrix", call. = FALSE)
  }
  if (length(group) != ncol(counts)) {
    stop("`group` must have length equal to ncol(counts)", call. = FALSE)
  }

  group <- as.factor(group)
  levels_group <- levels(group)
  if (length(levels_group) != 2) {
    stop("`group` must have exactly two distinct levels, found: ",
      length(levels_group),
      call. = FALSE
    )
  }

  idx_a <- which(group == levels_group[1])
  idx_b <- which(group == levels_group[2])

  gene_names <- rownames(counts)
  if (is.null(gene_names)) {
    gene_names <- paste0("gene", seq_len(nrow(counts)))
  }

  n_genes <- nrow(counts)
  log2fc <- numeric(n_genes)
  pvalue <- numeric(n_genes)

  for (i in seq_len(n_genes)) {
    x_a <- counts[i, idx_a]
    x_b <- counts[i, idx_b]

    log2fc[i] <- log2(mean(x_b) + pseudocount) - log2(mean(x_a) + pseudocount)

    pvalue[i] <- tryCatch(
      stats::t.test(x_a, x_b)$p.value,
      error = function(e) NA_real_
    )
  }

  padj <- stats::p.adjust(pvalue, method = "BH")
  result <- data.frame(
    gene = gene_names,
    log2fc = log2fc,
    pvalue = pvalue,
    padj = padj,
    row.names = NULL,
    stringsAsFactors = FALSE
  )
  result[order(result$padj), ]
}
