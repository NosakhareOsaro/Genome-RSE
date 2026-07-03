# Data source

**Real, public data.** `splice.data` (and its accompanying `splice.names`
metadata file) is the UCI Machine Learning Repository's "Molecular Biology
(Splice-junction Gene Sequences)" dataset, retrieved 2026-07-03 from:

- <https://archive.ics.uci.edu/ml/machine-learning-databases/molecular-biology/splice-junction-gene-sequences/splice.data>
- <https://archive.ics.uci.edu/ml/machine-learning-databases/molecular-biology/splice-junction-gene-sequences/splice.names>

Both files are cached in this repo (rather than fetched at train/CI time)
so training is reproducible without depending on `archive.ics.uci.edu`
uptime, matching the provenance approach used for sample data in earlier
phases (see `plugins/jbrowse2-sv-tracks/backend/data/DATA_SOURCE.md`).

## Provenance

Every example is real primate DNA taken from GenBank 64.1: the `EI` and
`IE` categories are every annotated "split gene" (exon/intron boundary)
for primates in that GenBank release; the `N` (neither) category is drawn
from sequences known *not* to contain a splicing site. Donated by G.
Towell, M. Noordewier, and J. Shavlik (University of Wisconsin-Madison /
Rutgers), 1992. See `splice.names` for the full donor citation list.

## Shape

3,190 instances, each a 60-nucleotide window plus a class label:

- `EI` (767 instances) — intron→exon boundary ("acceptor")
- `IE` (768 instances) — exon→intron boundary ("donor")
- `N` (1,655 instances) — neither

The 60-position sequence alphabet is `{A, C, G, T}` plus four IUPAC
ambiguity codes that appear in a handful of instances (`D`, `N`, `R`, `S`
— not to be confused with the `N` *class* label above, which denotes
"non-splice-site", not the ambiguous-nucleotide code). `training/features.py`
one-hot encodes over this full 8-symbol observed alphabet rather than
assuming a clean 4-letter alphabet, specifically because of these codes.

## Why this task, for this phase

Splice-junction prediction — given a window of DNA, is the center a
donor/acceptor/neither — is a classic, well-posed bioinformatics
classification problem with a small, clean, public, real-data benchmark.
That combination (real biological data, small enough to train in seconds,
a defined multi-class target) makes it a good fit for Phase 4's purpose:
demonstrating an MLOps pipeline (train → register → promote → serve →
deploy), not building a novel or production-grade splice predictor. See
`services/model-serving/README.md` for the explicit "demonstration
stand-in" scope note.
