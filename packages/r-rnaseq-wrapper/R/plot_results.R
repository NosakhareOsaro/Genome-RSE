#' Plot a volcano plot of differential expression results
#'
#' Draws a basic volcano plot (log2 fold change vs. -log10 adjusted
#' p-value) from the output of [run_deg()], using base R graphics only.
#' Genes passing both the fold-change and significance thresholds are
#' highlighted.
#'
#' @param deg_results A data.frame as returned by [run_deg()], with
#'   columns `log2fc` and `padj`.
#' @param padj_threshold Adjusted p-value significance threshold.
#'   Default `0.05`.
#' @param log2fc_threshold Absolute log2 fold-change threshold. Default `1`.
#' @param ... Additional arguments passed on to [graphics::plot()].
#'
#' @return Invisibly, a logical vector indicating which genes were
#'   highlighted as significant.
#'
#' @examples
#' deg <- data.frame(
#'   gene = paste0("gene", 1:5),
#'   log2fc = c(-3, -0.2, 0.1, 2.5, 4),
#'   pvalue = c(0.001, 0.6, 0.9, 0.02, 0.0001),
#'   padj = c(0.005, 0.7, 0.95, 0.04, 0.0005)
#' )
#' plot_results(deg)
#'
#' @export
plot_results <- function(deg_results, padj_threshold = 0.05, log2fc_threshold = 1, ...) {
  required_cols <- c("log2fc", "padj")
  missing_cols <- setdiff(required_cols, names(deg_results))
  if (length(missing_cols) > 0) {
    stop("`deg_results` is missing required column(s): ",
      paste(missing_cols, collapse = ", "),
      call. = FALSE
    )
  }

  neg_log10_padj <- -log10(deg_results$padj)
  is_significant <- !is.na(deg_results$padj) &
    deg_results$padj < padj_threshold &
    abs(deg_results$log2fc) > log2fc_threshold

  point_colors <- ifelse(is_significant, "red", "grey60")

  graphics::plot(
    deg_results$log2fc,
    neg_log10_padj,
    col = point_colors,
    pch = 20,
    xlab = "log2 fold change",
    ylab = "-log10(adjusted p-value)",
    main = "Volcano plot",
    ...
  )
  graphics::abline(h = -log10(padj_threshold), lty = 2, col = "blue")
  graphics::abline(v = c(-log2fc_threshold, log2fc_threshold), lty = 2, col = "blue")

  invisible(is_significant)
}
