# rnaseqwrapper

<!-- badges: start -->
[![R-CMD-check](https://github.com/NosakhareOsaro/Genome-RSE/actions/workflows/r-rnaseq-wrapper-ci.yml/badge.svg)](https://github.com/NosakhareOsaro/Genome-RSE/actions/workflows/r-rnaseq-wrapper-ci.yml)
[![Codecov test coverage](https://codecov.io/gh/NosakhareOsaro/Genome-RSE/branch/main/graph/badge.svg?flag=r-rnaseq-wrapper)](https://codecov.io/gh/NosakhareOsaro/Genome-RSE)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)
<!-- badges: end -->

A small set of wrapper functions implementing a **basic** RNA-seq
differential expression workflow, built as a Phase 1 portfolio package.

> **Scope note:** `run_deg()` uses a per-gene Welch t-test with
> Benjamini-Hochberg adjustment, not a negative-binomial model like
> DESeq2 or edgeR. This keeps the package dependency-free (no
> Bioconductor), but it is a teaching/demonstration implementation, not
> a replacement for a production differential expression tool.

## Installation

```r
# install.packages("pak")
pak::pak("NosakhareOsaro/Genome-RSE", subdir = "packages/r-rnaseq-wrapper")
```

## Usage

```r
library(rnaseqwrapper)

counts_path <- system.file("extdata", "sample_counts.csv", package = "rnaseqwrapper")
counts <- load_counts(counts_path)

cpm <- normalize_counts(counts, method = "cpm")

group <- c("control", "control", "control", "treated", "treated", "treated")
deg <- run_deg(counts, group)
head(deg)

plot_results(deg)
```

## Sample data

`inst/extdata/sample_counts.csv` is small, hand-authored synthetic data
(not from a real experiment) — see `inst/extdata/DATA_SOURCE.md` for
details.

## Documentation

Function reference: see the `man/` pages, or the pkgdown site config in
`_pkgdown.yml` (build locally with `pkgdown::build_site()`).

## Test coverage

Coverage is measured with [covr](https://covr.r-lib.org/):

```r
covr::package_coverage()
```

The Codecov badge above requires connecting this repository at
[codecov.io](https://codecov.io) and uploading `covr`'s output from CI
(not yet wired up — badge will show "unknown" until that's done).
