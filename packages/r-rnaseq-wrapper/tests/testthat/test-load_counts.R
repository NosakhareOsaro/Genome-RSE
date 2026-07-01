test_that("load_counts reads a well-formed CSV into a numeric matrix", {
  path <- system.file("extdata", "sample_counts.csv", package = "rnaseqwrapper")
  counts <- load_counts(path)

  expect_true(is.matrix(counts))
  expect_true(is.numeric(counts))
  expect_equal(dim(counts), c(6, 6))
  expect_equal(rownames(counts), paste0("gene", 1:6))
  expect_equal(
    colnames(counts),
    c("control_1", "control_2", "control_3", "treated_1", "treated_2", "treated_3")
  )
  expect_equal(unname(counts["gene1", "control_1"]), 100)
})

test_that("load_counts errors on a missing file", {
  expect_error(load_counts("does/not/exist.csv"), "File not found")
})

test_that("load_counts errors on non-numeric sample columns", {
  tmp <- tempfile(fileext = ".csv")
  on.exit(unlink(tmp))
  writeLines(c("gene,sample1,sample2", "gene1,10,not_a_number"), tmp)

  expect_error(load_counts(tmp), "must be numeric")
})
