<p align="center">
  <img src="docs/images/focipy_logo.png" alt="FociPy Logo" width="500">
</p>

**FociPy** is an open-source Python pipeline for the automated analysis of DNA repair protein recruitment kinetics at laser-induced damage sites. It processes timelapse fluorescence microscopy data from microirradiation experiments, extracts normalized intensity curves, and exports publication-ready quantitative results.

Designed for analyzing **XRCC1** (single-strand break marker) and **53BP1** (double-strand break marker) accumulation in HeLa cells, but the modular architecture allows adaptation to other fluorescently-tagged repair proteins.

_This software is being developed as part of a master's thesis in Molecular and Cellular Biophysics at the Jagiellonian University (Faculty of Biochemistry, Biophysics and Biotechnology)._

![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=Python)
![Stage](https://img.shields.io/badge/project-architecture_design-orange)
![Last Commit](https://img.shields.io/github/last-commit/stanuch/focipy)

> [!WARNING]
> **UNDER DEVELOPMENT – NOT YET USABLE**
>
> FociPy is currently in the architecture design phase. The module structure is defined,
> but core algorithms are not yet implemented. Do not use for quantitative analysis.

## Scientific context

In microirradiation experiments, a focused laser beam (488 nm) induces localized DNA damage within a single cell nucleus. Fluorescently-tagged repair proteins (e.g. GFP-XRCC1) are recruited to the damage site, forming a visible accumulation ("focus") that can be tracked over time. Traditional analysis in ImageJ/FIJI relies on manual ROI selection — a process that is subjective, time-consuming, and difficult to scale. FociPy will be a fully automated extraction of recruitment kinetics from raw microscopy files, using the normalization formula:

$$I_{norm}(t) = \frac{I_{foci}(t) - I_{bg}}{I_{nuc}(t) - I_{bg}}$$

where:

- $I_{foci}(t)$ — mean intensity within the repair focus ROI at time $t$
- $I_{nuc}(t)$ — mean intensity of the entire nucleus (reference pool)
- $I_{bg}$ — mean background intensity (outside all nuclei)

This normalization corrects for variable expression levels (transient transfection) and photobleaching effects.

## Project goals

- Automated segmentation of cell nuclei from DAPI/Hoechst-stained timelapse images
- Tracking of laser-induced repair foci through timelapse sequences (center-of-mass drift correction)
- Extraction of normalized recruitment kinetics curves
- Quantitative analysis: half-recruitment time ($t_{1/2}$), maximum intensity ($I_{max}$), plateau level
- Investigation of dose-dependent DNA damage response (488 nm laser power vs. recruitment dynamics)
- Batch processing with full audit trail (source file hashes, pipeline parameters, QC images)

## Experimental setup

| Parameter            | Value                                |
| -------------------- | ------------------------------------ |
| **Cell line**        | HeLa (transient transfection)        |
| **Markers**          | GFP-XRCC1 (SSB), GFP-53BP1 (DSB)     |
| **Microscope**       | Leica TCS SP5 FLIM                   |
| **Objective**        | HCX PL APO 63x/1.40 OIL              |
| **Damage induction** | Point microirradiation, 488 nm laser |
| **Nuclear stain**    | DAPI / Hoechst                       |
| **Data format**      | Leica .lif (native)                  |

## Module overview

| Module              | Purpose                                                       |
| ------------------- | ------------------------------------------------------------- |
| `config.py`         | Pipeline parameters (dataclass + YAML)                        |
| `io_utils.py`       | Image loading (.lif, .tif), metadata extraction, file hashing |
| `preprocessing.py`  | Noise reduction, background subtraction                       |
| `segmentation.py`   | Nuclear segmentation (Otsu+Watershed, Cellpose)               |
| `kinetics.py`       | ROI tracking, intensity measurement, normalization            |
| `quantification.py` | Kinetic curve statistics (t_half, I_max)                      |
| `reporting.py`      | CSV/JSON export, experiment metadata, audit trail             |
| `visualization.py`  | Kinetics plots, segmentation overlays, QC panels              |
| `pipeline.py`       | Orchestration of the full workflow                            |

## Tech stack

| Category                    | Tools                              |
| --------------------------- | ---------------------------------- |
| **Core**                    | Python 3.10+, NumPy, Pandas, SciPy |
| **Image processing**        | scikit-image, tifffile             |
| **Leica file support**      | readlif                            |
| **Segmentation (optional)** | Cellpose                           |
| **Visualization**           | Matplotlib, Napari (QC)            |
| **Configuration**           | PyYAML, dataclasses                |

## Current status

- Project stage: **architecture design**
- Module structure: **defined**
- Core implementation: **not started**
- Validation: **not started**

## Disclaimer

This project is a research prototype developed for academic purposes (master's thesis).
No guarantees are made regarding correctness, completeness, or suitability of the results at the current development stage.

**Detailed documentation, including usage instructions (USAGE.md), methodology (METHODS.md), and changelogs (CHANGELOG.md), can be found in the [`docs/`](docs/) directory.**
