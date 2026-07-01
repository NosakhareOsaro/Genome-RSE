#' Load a gene-by-sample RNA-seq count matrix from a CSV file
#'
#' Reads a CSV file where the first column holds gene identifiers and the
#' remaining columns hold raw (integer) read counts per sample, and returns
#' a numeric matrix with genes as rows and samples as columns.
#'
#' @param path Path to a CSV file. The first column is used as row names
#'   (gene identifiers); all remaining columns must be numeric.
#'
#' @return A numeric matrix of raw counts, genes x samples.
#'
#' @examples
#' counts_path <- system.file("extdata", "sample_counts.csv", package = "rnaseqwrapper")
#' counts <- load_counts(counts_path)
#' dim(counts)
#'
#' @export
load_counts <- function(path) {
  if (!file.exists(path)) {
    stop("File not found: ", path, call. = FALSE)
  }

  df <- utils::read.csv(path, row.names = 1, check.names = FALSE)

  if (ncol(df) == 0) {
    stop("Count file must have at least one sample column", call. = FALSE)
  }

  is_numeric_col <- vapply(df, is.numeric, logical(1))
  if (!all(is_numeric_col)) {
    stop(
      "All sample columns must be numeric; found non-numeric column(s): ",
      paste(names(df)[!is_numeric_col], collapse = ", "),
      call. = FALSE
    )
  }

  counts <- as.matrix(df)
  storage.mode(counts) <- "numeric"
  counts
}
