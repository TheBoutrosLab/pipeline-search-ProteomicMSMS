# Pipeline tests

`nftest.yml` runs four integration cases across multiple samples: Comet,
Sage, MSFragger, and Comet without mzML reindexing. Each input CSV contains
the required `sample_name,path` columns, with two fractions for one sample
and one fraction each for two more samples. The cases use the standard SBP
configuration modules and real search executables. A run passes only if
Nextflow and all selected processes complete successfully.

Copy `.env-template` to ignored `.env`. Keep its Nextflow version and parser
settings, and set `TEST_DATA_DIR=/data/user/czhu/data/pipeline_test_data` as
the only test-data variable. The mzML files,
target-decoy FASTA under `database/`, and `MSFragger-4.4.1.jar` are resolved
relative to that directory. The test configs use the FASTA's `rev_` decoy
prefix. Run
from the repository root inside a Slurm job, for example:

```bash
bash test/run-nftest.sh test-integration-comet
bash test/run-nftest.sh test-integration-sage
bash test/run-nftest.sh test-integration-msfragger
bash test/run-nftest.sh test-integration-no-reindex
```

The CSV environment expander fails if `TEST_DATA_DIR` is unset. The
MSFragger case leaves the optional spectrum-reference repair disabled.
