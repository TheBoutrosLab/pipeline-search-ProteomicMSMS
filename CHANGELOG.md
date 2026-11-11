# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
[unreleased]: https://github.com/TheBoutrosLab/pipeline-search-ProteomicMSMS/compare/v1.1.0...HEAD
