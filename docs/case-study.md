# GenomeRSE Phase 5: original contributions — a case study

This document summarizes four work packages carried out in Phase 5 of
the GenomeRSE project, each producing a real, externally-verifiable
artifact on a system outside this repository's control. It is written
for a reader who may not be a bioinformatician, may not be familiar with
the specific tools named below, and may not have read the rest of this
repository — each section explains enough context to be read on its own.

**What this document is not:** a claim of novel research, or of having
solved a previously unsolved problem. Every item below is either a bug
report against existing software, a workflow registration, a package
publication, or a research-data archive registration — all standard
categories of software engineering activity. What follows is a factual
account of what was done and what it produced, with a link to the real
artifact for each, so a reader can verify any of it directly rather than
relying on this document's description of it.

## Background

[GenomeRSE](../README.md) is a four-phase software portfolio: two
packaged libraries (Python and R, for genomic-data processing tasks), an
async web API implementing part of a healthcare data standard (FHIR R4),
a plugin for an existing open-source genome browser (JBrowse2), and a
small machine-learning model deployed via a Kubernetes-based pipeline.
Each phase was built, tested, and verified against real running
infrastructure rather than assumed to work from a passing test suite
alone. This Phase 5 work builds on that foundation: rather than adding
more repository scope, it takes findings and artifacts already produced
in Phases 1-4 and puts them in front of external systems and external
reviewers who have no connection to this project.

## 1. A bug report filed against JBrowse2

[JBrowse2](https://jbrowse.org/jb2/) is an open-source genome browser
widely used in genomics research; the underlying codebase is
[GMOD/jbrowse-components](https://github.com/GMOD/jbrowse-components).
Phase 3 of this project built a small plugin for JBrowse2 following its
own official plugin-development template.

**The technical gap.** JBrowse2 allows third-party plugins to reuse a
fixed set of its own internal building blocks (base classes for adapters,
renderers, and similar extension points) without those plugins having to
bundle a second copy of JBrowse2's own code. This works by exposing those
building blocks on a shared global object at runtime. While building the
Phase 3 plugin, extending one of these shared base classes the way the
official plugin template's own documentation shows produced no error
during development or in a build — but threw a runtime error
(`Class extends value #<Object> is not a constructor or null`) the first
time the plugin actually ran in a browser.

**What was done.** Rather than treat the earlier Phase 3 workaround as
settled, Phase 5 re-investigated it from scratch: a brand-new copy of the
current JBrowse2 release was assembled independently (not reusing the
project's own already-patched plugin code), and the shared global object
was inspected directly in a real browser to see its actual contents.
This confirmed the problem was still present, and — checking a wider set
of the shared building blocks than the original Phase 3 investigation
had — found it affects four specific base classes, not the one
originally noticed. The two affected and unaffected source files were
then compared directly on GitHub; both use identical code patterns,
ruling out an explanation based on how the individual files are written.
The official plugin template's own build configuration was read to
confirm the problem is reachable by anyone following its standard,
documented setup, not only by an unusual configuration. A search of
GMOD/jbrowse-components' existing issues did not turn up an existing
report describing this specific problem, though a related, different
report of the same general category
([#5002](https://github.com/GMOD/jbrowse-components/issues/5002), fixed
by a maintainer the same day it was filed) showed the maintainers do act
on this category of bug.

**Artifact.** [GMOD/jbrowse-components#5594](https://github.com/GMOD/jbrowse-components/issues/5594),
filed 2026-07-04. As of this writing, the issue is open and has not yet
received a maintainer response.

**What this shows.** The report documents a reproducible bug, filed
after re-confirming it against current code (not assumed carried over
from earlier work), with its scope mapped out and an alternative
explanation checked and ruled out before submission. It is a bug report
on an active external project, not a resolved contribution — the outcome
depends on the maintainers, and this document will be updated if and
when they respond.

## 2. A workflow registered on Dockstore

[Dockstore](https://dockstore.org) is a public registry used in
bioinformatics for sharing computational workflows in a form other
research groups can find, inspect, and run themselves, independent of
where the workflow's source code happens to live.

**The underlying artifact.** Phase 3 of this project built a small
workflow, written in WDL (Workflow Description Language), that prepares
a genomic data file (sorting and indexing it) before it can be displayed
by a genome browser. That workflow had already been executed
successfully against real data using real container images, and a
Dockstore-compatible descriptor file for it already existed in the
repository — but it had never been registered on Dockstore itself.

**What was done.** Dockstore's GitHub integration was installed and
granted access to this repository. The workflow did not appear on
Dockstore afterward, including after using Dockstore's manual refresh
option repeatedly. Rather than guess at a cause, the descriptor file's
syntax was checked line-by-line against Dockstore's current published
documentation (it was correct), and Dockstore's own per-repository sync
log was checked (it was empty, indicating no sync attempt had been made
at all, rather than a failed one). Dockstore's documentation states that
its GitHub integration is triggered by new commits, and that a repository
whose descriptor file already existed before the integration was
installed may need a new commit to trigger the first synchronization.
A small, genuinely useful field (a one-line workflow description) was
added to the descriptor file for exactly this purpose, and after that
commit was pushed, the workflow synchronized and was published.

**Artifact.** [prepare-sv-track-data on Dockstore](https://dockstore.org/workflows/github.com/NosakhareOsaro/Genome-RSE/prepare-sv-track-data:main?tab=info),
published 2026-07-04.

**What this shows.** Registering an already-correct, already-tested
workflow on a public registry still required diagnosing why an expected
step (automatic synchronization) did not happen, using the registry's
own logs and documentation rather than trial and error, before making a
change.

## 3. A package published to PyPI

[PyPI](https://pypi.org) (the Python Package Index) is the standard
public registry for distributing installable Python software; publishing
a package there is what makes `pip install <package-name>` work for
anyone, without them needing access to this repository.

**The underlying artifact.** Phase 1 of this project built a small
Python package containing a VCF (genomic variant file) annotation
helper, a minimal validator for a healthcare data format (FHIR), and a
plugin for a quality-control reporting tool (MultiQC). The package
existed and was tested, but had not been published anywhere installable.

**What was done.** The package's originally-planned public name,
`genomics-utils`, was confirmed available on PyPI, but was judged too
generic on review: a reader encountering a package with that name on
PyPI, without prior context, would have no way to tell it apart from a
general-purpose production library, when its own documentation is
explicit that it is a small, demonstration-scoped tool. The package was
renamed to `genomerse-genomics-utils` before anything was published
anywhere (only the published name changed; the code and its internal
module name were unaffected). The package's metadata (author, license,
project links, and the text that would be displayed as its PyPI
description) was checked field-by-field, and validated using the same
tool PyPI itself uses to check that description text will display
correctly. A complete rehearsal publish was then done to PyPI's separate
test system (test.pypi.org), under the final package name, and the
installed result was verified by starting a new, empty Python
environment, installing the package into it exactly as any external user
would, and calling its actual functions on sample input to confirm they
produced correct output — not only confirming that the package could be
imported. Only after that rehearsal succeeded was the package published
to the real, public PyPI, and the same fresh-environment install and
function-level check was repeated against the real published version.

**Artifact.** [genomerse-genomics-utils 0.1.0 on PyPI](https://pypi.org/project/genomerse-genomics-utils/0.1.0/),
published 2026-07-04. `pip install genomerse-genomics-utils` installs it
for anyone, from the public internet.

**What this shows.** The publication was preceded by a naming decision
made explicitly (rather than defaulting to the first available name), a
metadata check using PyPI's own validation tooling, and a full rehearsal
on a separate test system before the real, irreversible publish step —
PyPI does not allow a published package name and version to be deleted
and reused once published.

## 4. A Zenodo DOI archiving this repository

[Zenodo](https://zenodo.org) is a research-data archive that, through an
integration with GitHub, can automatically archive a snapshot of a
GitHub repository at the point of a release and assign it a DOI (a
persistent, citable identifier of the kind used to cite datasets and
software in academic work). This is standard practice for making
research software formally citable; it does not depend on the software
being novel.

**What was done.** The metadata files Zenodo reads to describe the
archive (`CITATION.cff` and `.zenodo.json`, both at this repository's
root) were prepared ahead of time, and the repository was tagged
`v1.1.0-original-contributions` to mark all five Phase 5 work packages,
including this document, as complete. The GitHub Release that triggers
Zenodo's archiving was cut from that tag — but the one-time step
connecting this specific repository to Zenodo had not actually been
completed before that release was published, so Zenodo never received
the event and no DOI was minted. The repository was then connected to
Zenodo for real, and a second release, `v1.1.1`, was cut from a small
follow-up commit (a version-number bump only, no code or functional
changes) specifically to produce a fresh `release.published` webhook
event for Zenodo to act on.

**Artifact.** [10.5281/zenodo.21197886](https://doi.org/10.5281/zenodo.21197886),
minted 2026-07-04. This is a Zenodo "concept DOI," which always resolves
to the latest archived version (`v1.1.1` at the time of writing) rather
than being pinned to one snapshot — the standard way to cite software
that may have later versions. The archived record's author name and
license were confirmed to match this project's real metadata before
this section was written.

**What this shows.** The archive exists and is independently resolvable
through the DOI system used for citing software and data in academic
contexts. Getting there required noticing that a completed-looking step
(tagging and releasing) had not actually produced the expected result,
and fixing the actual cause (the GitHub-Zenodo connection, not the
release itself) rather than repeating the same release again unchanged.

## Method

Each of the four items above followed the same underlying approach used
throughout this project: before asserting that something was broken,
missing, or fixed, check it directly against the real, current state of
the external system in question, rather than against an assumption or an
earlier finding taken as still valid. In the JBrowse2 case, that meant
re-testing against a freshly assembled current build rather than
trusting a two-phase-old finding. In the Dockstore case, it meant reading
the actual sync logs rather than guessing at why nothing appeared. In the
PyPI case, it meant rehearsing the exact real command on a separate test
system before running it for real. In the Zenodo case, it meant noticing
that a release had been published without producing the expected
archive, and fixing the actual cause rather than repeating the same step
again unchanged. None of the four represents a solved research problem;
they represent standard categories of engineering work — reporting a
bug, registering a workflow, publishing a package, archiving a release —
carried out by checking each step against the real system involved
rather than assuming it would behave as expected.
