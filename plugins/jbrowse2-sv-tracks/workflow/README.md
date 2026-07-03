# prepare_sv_track_data.wdl

A Dockstore-compatible WDL workflow that coordinate-sorts and
bgzip+tabix-indexes a VCF, and coordinate-sorts and indexes a BAM —
exactly the preprocessing `sv-tracks-backend`/the JBrowse2 plugin expect
from source data before serving/visualizing it. **Not registered live
on [dockstore.org](https://dockstore.org)** as part of this repo's
automation; see the repo-root `.dockstore.yml` for the descriptor
Dockstore's GitHub App would pick up if/when it is.

## Run locally

Requires Docker and [miniwdl](https://github.com/chanzuckerberg/miniwdl)
(`pip install miniwdl`) or [Cromwell](https://cromwell.readthedocs.io/).

```bash
miniwdl run prepare_sv_track_data.wdl -i test.inputs.json
```

> **Note:** if you hit a Docker error like `invalid mount config for
> type "bind": ... operation not permitted`, it's a macOS Docker
> Desktop file-sharing restriction on the directory the repo happens to
> be checked out under (we hit the same thing under `~/Downloads` in
> Phase 2) — not a bug in the workflow. Run from a directory Docker
> Desktop is allowed to bind-mount (e.g. copy the repo under `/tmp` or
> add the parent directory in Docker Desktop's Settings > Resources >
> File sharing).

`test.inputs.json` points at this repo's own sample data
(`backend/data/sv-demo.vcf`, `backend/data/volvox-sorted.bam`).
Verified end-to-end: both tasks complete successfully and produce a
genuinely queryable, tabix-indexed VCF and a coordinate-sorted, indexed
BAM (checked with pysam, not just "exit code 0").

One real bug found while doing that verification: the initial version
called the standalone `tabix` binary, which the `staphb/bcftools`
Docker image doesn't include (`tabix: command not found`, exit 127).
Fixed by using `bcftools index --tbi` instead, which builds the same
tabix-compatible `.tbi` index without needing a separate tool.
