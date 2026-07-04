# WP3: Dockstore workflow registration

**Status:** Published, live.
**Artifact:** [dockstore.org/workflows/github.com/NosakhareOsaro/Genome-RSE/prepare-sv-track-data](https://dockstore.org/workflows/github.com/NosakhareOsaro/Genome-RSE/prepare-sv-track-data:main?tab=info)
**Published:** 2026-07-04

## What this is

`plugins/jbrowse2-sv-tracks/workflow/prepare_sv_track_data.wdl` -- a small
WDL workflow that coordinate-sorts and bgzip+tabix-indexes a VCF, and
coordinate-sorts and indexes a BAM, using `bcftools`/`samtools` in public
containers. Built in Phase 3 and actually run end-to-end with `miniwdl`
against real Docker containers and this repo's own sample data at the
time (not just syntax-checked) -- see
`plugins/jbrowse2-sv-tracks/workflow/README.md` for that verification,
including a real bug it caught (`bcftools` image missing the standalone
`tabix` binary, fixed with `bcftools index --tbi`). The `.dockstore.yml`
descriptor at the repo root has existed since Phase 3; this work package
is about actually registering and publishing it live, which hadn't been
done.

## What actually happened

1. Installed and correctly scoped the Dockstore GitHub App to
   `NosakhareOsaro/Genome-RSE`.
2. The workflow did not appear under Published or Unpublished on
   `dockstore.org/my-workflows`, even after repeatedly clicking "Refresh
   Organization."
3. Investigated rather than guessing: confirmed `.dockstore.yml`'s syntax
   and schema were correct against Dockstore's own current documentation
   (fetched fresh -- leading-slash paths, required/optional keys, `name`
   field usage all matched their real example exactly), and checked
   Dockstore's "App Logs" for this organization, which showed nothing at
   all -- not an error, just no record of any sync attempt.
4. **The actual, documented cause**: Dockstore's GitHub App sync is
   webhook-driven, firing on push/release events. `.dockstore.yml`
   already existed in this repo *before* the app was installed, so there
   had been no push since installation to trigger the first sync.
   "Refresh Organization" is a different, account-level action (detecting
   newly added repos/orgs) and doesn't retroactively re-scan existing
   files for a repo already connected. Dockstore's own troubleshooting
   docs state this directly: "if...this is your first time installing
   the app, you may need to push another commit...to activate the sync."
5. Fixed by adding the optional `topic` field to `.dockstore.yml` (a
   real, documented field Dockstore displays as the workflow's one-line
   description -- not a throwaway change) and pushing that commit, which
   produced the push Dockstore was waiting for. The workflow synced and
   was then manually published (sync alone doesn't make a workflow
   public; Dockstore requires an explicit publish step).

This is worth recording plainly rather than glossing over: registering an
already-correct, already-verified workflow on Dockstore still took a real
troubleshooting pass, because "install the app and it just works" isn't
quite how first-time GitHub App sync behaves. That's a minor, practical,
documented gotcha -- not a novel discovery -- but it's exactly the kind
of real detail a contribution record like this should keep, rather than
only showing the clean end state.

## Why this matters

Dockstore is the standard registry for sharing bioinformatics workflows
(WDL/CWL/Nextflow) in a form other labs and pipelines can discover, cite,
and directly launch -- registering here is standard practice done for
real, not a novel contribution, but it is a genuine, independently
checkable artifact: a live, public workflow page, backed by a workflow
that was actually executed and verified, not just described.
