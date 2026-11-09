# Changelog

All notable changes to the **FociPy** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-11-09

### Added

- **YAML configuration & provenance (`config.py`)**:
  - Implemented `PipelineConfig` and typed sub-dataclasses (`SegmentationConfig`, `KineticsConfig`, `PreprocessingConfig`, `OutputConfig`) with `from_yaml`, `to_yaml`, `from_dict`, and `to_dict` serialization for reproducible analysis runs.
- **Fast binary Leica `.lif` XML parser & loader (`io_utils.py`)**:
  - `extract_lif_xml`: reads only the UTF-16-LE XML header directly from binary `.lif` files in milliseconds without loading pixel data.
  - `parse_lif_metadata`: extracts spatial calibration (`pixel_size_um`, `fov_um`), hardware/optical settings (`zoom`, `magnification`, `pinhole_airy`, `scan_speed_hz`, `line_average`, `detector_gain_v`, `emission_band_nm`, imaging & bleach laser wavelengths and powers), frame timestamps from 64-bit Windows `FILETIME` ticks, pre-bleach frame counts, and laser microirradiation coordinates (`LaserCoordinate`).
  - Automatic concatenation of multi-phase FRAP acquisitions (`FRAP Series` + `FRAP Pb2 Series` + `FRAP Pb3 Series`) along the time axis `T` (`merge_pb_series=True`), including filtering of empty placeholder `Pb2` series from aborted runs.
  - Automatic detection and filtering of uncalibrated screenshot series (`Snapshot`) while linking them to their parent experiments via `associated_snapshots`.
  - `load_lif_series`: loads and concatenates `(T, C, Y, X)` fluorescence arrays across merged FRAP sub-series by index or name.
  - `catalog_lif_files`: recursively scans `.lif` directories (e.g. `data/raw`) and exports a 38-column metadata inventory to CSV (`data/processed/raw_series_catalog.csv`).
- **Interactive visualization (`visualization.py`)**:
  - `view_in_napari` and `view_in_matplotlib`: interactive timelapse viewers with overlaid laser target crosshairs (`+`), circular ROI measurement regions, and real-time phase status (`PRE-BLEACH`, `POST-BLEACH (Pb1)`, `POST-BLEACH (Pb2)`).
  - `list_lif_series` and `view_lif_series` high-level inspection helpers.
- **Command-line interface (`__main__.py`)**:
  - Added `focipy info`, `focipy view`, `focipy catalog`, and `focipy help` subcommands with English bioinformatics-style manual and `--version` support.
- **Documentation**:
  - Documented `.lif` binary parsing, coordinate transformations, multi-phase FRAP merging, and configuration provenance in `docs/METHODS.md` and `docs/USAGE.md`.

---

## [0.3.1] - 2026-03-27

### Changed

- Rewrote `README.md` — cleaner structure, updated badges, installation instructions.
- Simplified `pyproject.toml` — fixed `build-backend`, minimal config.
- Activated `config/default_config.yaml` with real default values (was fully commented out).
- Cleaned up docstrings and TODO comments across modules.

### Added

- `__init__.py` — package docstring and `__version__` via `importlib.metadata`.
- `environment.yml` for conda environment setup.
- Ruff badge in README.

---

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
