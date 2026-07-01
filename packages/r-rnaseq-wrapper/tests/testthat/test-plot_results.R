deg_results <- data.frame(
  gene = paste0("gene", 1:5),
  log2fc = c(-3, -0.2, 0.1, 2.5, 4),
  pvalue = c(0.001, 0.6, 0.9, 0.02, 0.0001),
  padj = c(0.005, 0.7, 0.95, 0.04, 0.0005)
)

test_that("plot_results runs without error and flags the expected genes", {
  grDevices::pdf(NULL)
  on.exit(grDevices::dev.off())

  result <- plot_results(deg_results)

  expect_type(result, "logical")
  expect_length(result, nrow(deg_results))
  expect_equal(result, c(TRUE, FALSE, FALSE, TRUE, TRUE))
})

test_that("plot_results respects custom thresholds", {
  grDevices::pdf(NULL)
  on.exit(grDevices::dev.off())

  result <- plot_results(deg_results, padj_threshold = 0.01, log2fc_threshold = 3)
  expect_equal(result, c(FALSE, FALSE, FALSE, FALSE, TRUE))
})

test_that("plot_results errors when required columns are missing", {
  expect_error(
    plot_results(data.frame(log2fc = 1)),
    "missing required column"
  )
})
