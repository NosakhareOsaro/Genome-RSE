# Test/example data provenance

## `sample_counts.csv`

**Synthetic / hand-authored.** Not derived from any real RNA-seq
experiment or public dataset. 6 genes x 6 samples (3 "control", 3
"treated"), with `gene1` designed to be clearly down-regulated and
`gene2` clearly up-regulated in the treated group, and the remaining
genes roughly flat between groups. Values are small, deterministic
integers chosen to give predictable, easy-to-assert results in unit
tests and function examples.
