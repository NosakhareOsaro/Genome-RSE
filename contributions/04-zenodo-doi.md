# WP2: Zenodo DOI archiving this repository

**Status:** Minted, live.
**Artifact:** [10.5281/zenodo.21197886](https://doi.org/10.5281/zenodo.21197886)
**Minted:** 2026-07-04

## What this is

A [Zenodo](https://zenodo.org) archive of this repository, created
through Zenodo's GitHub integration (which snapshots a repository at the
point of a GitHub Release and assigns it a DOI -- a persistent, citable
identifier of the kind used to cite datasets and software in academic
work). This is standard practice for making research software formally
citable and does not depend on the software being novel. The metadata
files Zenodo reads (`CITATION.cff` and `.zenodo.json`, both at this
repository's root) were prepared as part of this work package.

## What actually happened

1. `CITATION.cff` and `.zenodo.json` were written/verified for the whole
   repository (not just one package), and validated -- `CITATION.cff`
   against the real CFF 1.2.0 schema via `cffconvert`, `.zenodo.json` as
   plain JSON.
2. The repository was tagged `v1.1.0-original-contributions`, marking
   all five Phase 5 work packages as complete, and a GitHub Release was
   cut from that tag.
3. No DOI appeared. The actual cause: the one-time step connecting this
   specific repository to Zenodo (via Zenodo's GitHub App/OAuth
   integration) had not actually been completed before that release was
   published -- so Zenodo never received a `release.published` webhook
   event for this repository at all. This wasn't a metadata or
   configuration error; the release itself was never seen by Zenodo.
4. The repository was connected to Zenodo for real. Since Zenodo only
   archives releases published *after* the connection exists, the
   already-published `v1.1.0-original-contributions` release could not
   be retroactively archived.
5. A follow-up tag, `v1.1.1`, was cut from a small commit that bumped
   the version fields in `CITATION.cff`/`.zenodo.json` (no code or
   functional changes) and a second GitHub Release was published from
   it, specifically to produce a fresh webhook event for the now-real
   connection to act on. This time Zenodo archived the release and
   minted a DOI.
6. Before treating this as done, the archive was checked directly:
   the DOI resolves (a real `curl` request against `doi.org` returns a
   302 to the Zenodo record), and the record's own metadata (fetched via
   Zenodo's API) confirms the correct title, the correct author name
   ("Osaro, Nosakhare"), the correct license (MIT), and version `1.1.1`.

This is recorded here plainly rather than showing only the clean end
state: the first release/tag looked complete by every signal available
in this repository (a real tag, a real Release, correct metadata files)
and still didn't produce an archive, because the actual missing piece
was on Zenodo's side, not this repository's. Diagnosing that required
checking Zenodo directly rather than assuming the metadata or release
process was at fault.

## Why this matters

Archiving a software release with a DOI is standard, widely used
practice for making research software citable -- not a novel
contribution -- but it produces a genuine, independently verifiable
artifact: a real DOI, resolvable by anyone, on a real academic archival
service, with metadata that can be checked directly against what this
repository actually is.
