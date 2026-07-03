# Test/demo data provenance

This directory mixes **real public data** and **hand-authored synthetic
data**. They are listed separately below — do not confuse one for the
other.

## Real, public data

Source: the [GMOD/jbrowse-components](https://github.com/GMOD/jbrowse-components)
repository's own `test_data/volvox/` directory — the small synthetic
"volvox" organism genome that the JBrowse2 project itself ships and
uses throughout its official tutorials and test suite. Retrieved
2026-07-03 from:

- `volvox.fa` / `volvox.fa.fai` — reference sequence, two contigs
  (`ctgA`, 50,001 bp; `ctgB`, 6,079 bp).
  <https://raw.githubusercontent.com/GMOD/jbrowse-components/main/test_data/volvox/volvox.fa>
- `volvox-sorted.bam` / `volvox-sorted.bam.bai` — real aligned sequencing
  reads against `ctgA`.
  <https://raw.githubusercontent.com/GMOD/jbrowse-components/main/test_data/volvox/volvox-sorted.bam>

These files are used exactly as published, no modifications.

## Synthetic, hand-authored data

- `sv-demo.vcf` (and its bgzipped+tabix-indexed form, `sv-demo.vcf.gz` /
  `sv-demo.vcf.gz.tbi`) — **NOT real data**. JBrowse2's own volvox demo
  VCF only contains SNPs/indels (no structural variants), and no small
  public VCF with real BND/DEL/DUP/INV records was found that shares
  coordinates with the volvox reference. This file was therefore
  hand-authored specifically for this demo: six schematic SV records
  (one DEL, one DUP, one INV, one BND breakend pair spanning `ctgA`/
  `ctgB`, and a second DEL) placed at arbitrary but in-range coordinates
  on the real volvox contigs above, purely so the plugin has something
  concrete to draw arcs between. The `REF` column uses a placeholder
  `N` throughout (the exact reference base is not meaningful for these
  synthetic records). Do not use this file for anything beyond
  exercising this demo's rendering code path.
