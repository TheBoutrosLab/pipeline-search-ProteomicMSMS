# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Migrate the pipeline license from GPL to BSD 3-Clause and update license documentation; shared code and third-party tools retain their respective licenses.

## [1.1.2] - 2026-11-19

### Changed

- Replace the Slurm-only NFTest shell runner with a Python runner for AWS, Pines, and local tests.

### Fixed

- Isolate OpenMS temporary files for each parallel MSFragger, Comet, and Sage search task.

## [1.1.1] - 2026-11-10

### Fixed

- Annotate MSFragger peptide identifications with source spectrum FAIMS compensation voltage before fraction merging, and fail on unresolved or conflicting FAIMS references.

## [1.1.0] - 2026-10-23

### Added

- Multiple samples or isobaric plexes per run, with fraction reindexing and result merging scoped to each sample.
- A required `sample_name,path` input CSV format for one or more samples per run.

## [1.0.0] - 2026-10-09

### Added

- Comet, MSFragger, and Sage search workflows.
- Schema validation, resource allocation, process logging, and container profiles.
- Per-fraction unfiltered idXML and MSFragger pepXML retention, merged idXML, and optional mzTab export.
- Fraction spectrum reindexing with globally unique scan numbers, preserving Thermo native ID syntax when present, and matching native-ID metadata, plus optional MSFragger spectrum reference repair.

[1.0.0]: https://github.com/TheBoutrosLab/pipeline-search-ProteomicMSMS/releases/tag/v1.0.0
[1.1.0]: https://github.com/TheBoutrosLab/pipeline-search-ProteomicMSMS/compare/v1.0.0...v1.1.0
[1.1.1]: https://github.com/TheBoutrosLab/pipeline-search-ProteomicMSMS/compare/v1.1.0...v1.1.1
[1.1.2]: https://github.com/TheBoutrosLab/pipeline-search-ProteomicMSMS/compare/v1.1.1...v1.1.2
[unreleased]: https://github.com/TheBoutrosLab/pipeline-search-ProteomicMSMS/compare/v1.1.2...HEAD
