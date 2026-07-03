version 1.0

## Prepares a VCF and BAM for serving by jbrowse2-sv-tracks/backend and
## visualizing in the jbrowse2-sv-tracks JBrowse2 plugin: coordinate-sorts
## and bgzip+tabix-indexes the VCF, and coordinate-sorts and indexes the
## BAM. Dockstore-compatible (see .dockstore.yml at the repo root); not
## registered live on dockstore.org as part of this repo's automation.

workflow PrepareSvTrackData {
  input {
    File vcf
    File bam
  }

  call SortAndIndexVcf {
    input:
      vcf = vcf,
  }

  call SortAndIndexBam {
    input:
      bam = bam,
  }

  output {
    File indexed_vcf_gz = SortAndIndexVcf.vcf_gz
    File indexed_vcf_gz_tbi = SortAndIndexVcf.vcf_gz_tbi
    File sorted_bam = SortAndIndexBam.bam_sorted
    File sorted_bam_bai = SortAndIndexBam.bam_sorted_bai
  }

  meta {
    description: "Sort/bgzip/index a VCF and sort/index a BAM ahead of serving them via sv-tracks-backend."
  }
}

task SortAndIndexVcf {
  input {
    File vcf
  }

  String base_name = basename(basename(vcf, ".gz"), ".vcf")

  command <<<
    set -euo pipefail
    bcftools sort ~{vcf} -Oz -o ~{base_name}.sorted.vcf.gz
    # bcftools index --tbi builds a tabix-compatible .tbi index without
    # needing the separate `tabix` binary, which the staphb/bcftools
    # image doesn't include (confirmed by actually running this task:
    # `tabix -p vcf ...` failed with "command not found").
    bcftools index --tbi ~{base_name}.sorted.vcf.gz
  >>>

  output {
    File vcf_gz = "~{base_name}.sorted.vcf.gz"
    File vcf_gz_tbi = "~{base_name}.sorted.vcf.gz.tbi"
  }

  runtime {
    docker: "staphb/bcftools:1.19"
    cpu: 1
    memory: "2 GB"
  }
}

task SortAndIndexBam {
  input {
    File bam
  }

  String base_name = basename(bam, ".bam")

  command <<<
    set -euo pipefail
    samtools sort -o ~{base_name}.sorted.bam ~{bam}
    samtools index ~{base_name}.sorted.bam
  >>>

  output {
    File bam_sorted = "~{base_name}.sorted.bam"
    File bam_sorted_bai = "~{base_name}.sorted.bam.bai"
  }

  runtime {
    docker: "staphb/samtools:1.19"
    cpu: 1
    memory: "2 GB"
  }
}
