counts <- matrix(
  c(10, 20, 30, 40),
  nrow = 2, byrow = TRUE,
  dimnames = list(c("gene1", "gene2"), c("sample1", "sample2"))
)

test_that("normalize_counts computes counts per million", {
  cpm <- normalize_counts(counts, method = "cpm")

  expect_equal(dim(cpm), dim(counts))
  expect_equal(unname(colSums(cpm)), c(1e6, 1e6))
  expect_equal(unname(cpm["gene1", "sample1"]), 10 / 40 * 1e6)
})

test_that("normalize_counts computes log2(cpm + 1) when requested", {
  cpm <- normalize_counts(counts, method = "cpm")
  log2cpm <- normalize_counts(counts, method = "log2cpm")

  expect_equal(log2cpm, log2(cpm + 1))
})

test_that("normalize_counts defaults to cpm", {
  expect_equal(normalize_counts(counts), normalize_counts(counts, method = "cpm"))
})

test_that("normalize_counts rejects non-matrix input", {
  expect_error(normalize_counts(as.data.frame(counts)), "must be a numeric matrix")
})

test_that("normalize_counts errors on a zero-count sample", {
  bad_counts <- matrix(c(0, 0, 5, 10), nrow = 2, dimnames = list(c("g1", "g2"), c("s1", "s2")))
  expect_error(normalize_counts(bad_counts), "zero total counts")
})
