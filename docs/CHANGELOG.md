# Changelog

All notable changes to the **FociPy** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-03-09

### Changed

- **Architecture redesign**: Reoriented project from static foci counting to kinetics pipeline for timelapse microirradiation analysis.
- Replaced `foci_detection.py` with `kinetics.py` (ROI tracking, intensity extraction, normalization).
- Rewrote `quantification.py` stubs for kinetic curve statistics (t_half, I_max, I_plateau) instead of foci counting.
- Updated `io_utils.py` to target `.lif` support and metadata extraction.
- Updated `visualization.py` stubs for kinetics plots and QC panels.
- Updated `pipeline.py` stubs for kinetics-specific orchestration.

### Added

- New module stubs: `config.py`, `kinetics.py`, `reporting.py`.
- `config/default_config.yaml` – template for pipeline parameters.
- `pyproject.toml` – modern Python packaging (replaces `requirements.txt`).

### Removed

- `foci_detection.py` (DoG/LoG detection – not applicable for point microirradiation).

---

## [0.2.0] - 2026-02-24

### Changed

- **Project restructuring**: Migrated from flat `src/` to `src/focipy/` package (src layout).
- Replaced `requirements.txt` with `pyproject.toml` (editable install via `pip install -e .`).
- Replaced `analysis.py` with modular `io_utils.py` (pathlib, tifffile, logging, type hints).

### Added

- New modules (stubs): `preprocessing.py`, `quantification.py`, `visualization.py`, `pipeline.py`.
- `config.py` with dataclass-based configuration and YAML loading support.
- `__main__.py` entry point (`python -m focipy`).
- `config/default_config.yaml` with documented default parameters.
- `tests/conftest.py` with synthetic test image fixtures.
- 4 notebook templates: data exploration, segmentation comparison, foci detection tuning, validation plots.

### Removed

- `src/analysis.py` (logic moved to `io_utils.py`).
- `notebooks/exploration.ipynb` (replaced by structured templates).

---

## [0.1.0] - 2026-01-07

### Added

- Created the initial project structure (folders: `data/raw`, `data/processed`, `src`).
- Implemented basic Image I/O module:
  - Function to traverse directory structures and find experiment folders.
  - Function to load images using `OpenCV`.

### Notes

- Currently, the program only displays the raw image; no processing is applied yet.
