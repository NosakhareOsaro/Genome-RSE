counts_path <- system.file("extdata", "sample_counts.csv", package = "rnaseqwrapper")
counts <- load_counts(counts_path)
group <- c("control", "control", "control", "treated", "treated", "treated")

test_that("run_deg returns one row per gene with the expected columns", {
  result <- run_deg(counts, group)

  expect_equal(nrow(result), nrow(counts))
  expect_named(result, c("gene", "log2fc", "pvalue", "padj"))
  expect_true(all(result$gene %in% rownames(counts)))
})

test_that("run_deg detects the designed up/down genes with low padj", {
  result <- run_deg(counts, group)
  by_gene <- stats::setNames(seq_len(nrow(result)), result$gene)

  gene1_row <- result[by_gene["gene1"], ]
  gene2_row <- result[by_gene["gene2"], ]

  expect_lt(gene1_row$log2fc, -1) # down-regulated in treated
  expect_lt(gene1_row$padj, 0.05)

  expect_gt(gene2_row$log2fc, 1) # up-regulated in treated
  expect_lt(gene2_row$padj, 0.05)
})

test_that("run_deg results are sorted by ascending padj", {
  result <- run_deg(counts, group)
  expect_equal(result$padj, sort(result$padj))
})

test_that("run_deg errors when group length doesn't match ncol(counts)", {
  expect_error(run_deg(counts, c("control", "treated")), "length equal to ncol")
})

test_that("run_deg errors when group doesn't have exactly two levels", {
  bad_group <- c("a", "b", "c", "a", "b", "c")
  expect_error(run_deg(counts, bad_group), "exactly two distinct levels")
})

test_that("run_deg assigns generic gene names when counts has no row names", {
  unnamed_counts <- counts
  rownames(unnamed_counts) <- NULL
  result <- run_deg(unnamed_counts, group)
  expect_true(all(grepl("^gene[0-9]+$", result$gene)))
})
