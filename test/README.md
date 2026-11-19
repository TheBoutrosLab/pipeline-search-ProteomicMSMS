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
prefix. Run from the repository root with NFTest, PyYAML, and python-dotenv
installed, for example:

```bash
python3 test/run-nftest.py test-integration-comet
python3 test/run-nftest.py test-integration-sage
python3 test/run-nftest.py test-integration-msfragger
python3 test/run-nftest.py test-integration-no-reindex
```

Set `NFT_CLUSTER=boutroslab_aws` inside an AWS Slurm job to run under
`$NFT_RUN_ROOT/$SLURM_JOB_ID`. Set `NFT_CLUSTER=pines` to use `$NFT_RUN_ROOT`
directly with Apptainer. With no cluster selected, the default Docker profile
is used. Relative `NFT_RUN_ROOT` paths resolve against the repository; an unset
root defaults there. Results go to `<run-root>/<test-case>/`, with temporary
files under `<run-root>/.nftest-temp/`.

The CSV environment expander fails if `TEST_DATA_DIR` is unset. The
MSFragger case leaves the optional spectrum-reference repair disabled.
