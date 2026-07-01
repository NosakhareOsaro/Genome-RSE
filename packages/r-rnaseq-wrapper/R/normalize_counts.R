#' Normalize a raw RNA-seq count matrix
#'
#' Applies simple library-size normalization. This is intentionally basic
#' (counts-per-million, optionally log2-transformed) rather than a full
#' Bioconductor-style normalization (e.g. DESeq2's median-of-ratios or
#' edgeR's TMM) so that this package has no Bioconductor dependencies.
#'
#' @param counts A numeric matrix of raw counts, genes x samples (as
#'   returned by [load_counts()]).
#' @param method One of `"cpm"` (counts per million) or `"log2cpm"`
#'   (`log2(cpm + 1)`).
#'
#' @return A numeric matrix of the same shape as `counts`, normalized.
#'
#' @examples
#' counts <- matrix(c(10, 20, 0, 5, 100, 200, 10, 50), nrow = 2, byrow = TRUE)
#' normalize_counts(counts, method = "cpm")
#'
#' @export
normalize_counts <- function(counts, method = c("cpm", "log2cpm")) {
  method <- match.arg(method)

  if (!is.matrix(counts) || !is.numeric(counts)) {
    stop("`counts` must be a numeric matrix", call. = FALSE)
  }

  lib_sizes <- colSums(counts)
  if (any(lib_sizes == 0)) {
    stop("Cannot normalize: sample(s) with zero total counts found", call. = FALSE)
  }

  cpm <- sweep(counts, 2, lib_sizes, FUN = "/") * 1e6

  if (method == "log2cpm") {
    return(log2(cpm + 1))
  }
  cpm
}
