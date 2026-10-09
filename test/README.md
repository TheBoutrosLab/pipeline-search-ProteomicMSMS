# Pipeline tests

`nftest.yml` runs four integration cases against two fractions of one sample or
plex: Comet, Sage, MSFragger, and Comet without mzML reindexing. Each case
uses the standard SBP configuration modules and real search executables. A run
passes only if Nextflow and all selected processes complete successfully.

Copy `.env-template` to ignored `.env` and set `SEARCH_MZML_F1`,
`SEARCH_MZML_F2`, `SEARCH_FASTA`, and `MSFRAGGER_JAR`. The FASTA must contain
target and decoy proteins compatible with the adapter indexing settings. Run
from the repository root inside a Slurm job, for example:

```bash
bash test/run-nftest.sh test-integration-comet
bash test/run-nftest.sh test-integration-sage
bash test/run-nftest.sh test-integration-msfragger
bash test/run-nftest.sh test-integration-no-reindex
```

The CSV environment expander fails if either fraction variable is unset. The
MSFragger case leaves the optional spectrum-reference repair disabled; its
pepXML attribute parser has focused tests in `test/test_msfragger_spectrum_refs.py`.
`test/smoke.sh` is a separate local workflow check using stand-in executables. `test/test_reindex_mzml.py` checks globally unique scan IDs, matching source-file format metadata, and updated precursor references.

