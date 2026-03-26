<p align="center">
  <img src="docs/images/focipy_logo.png" alt="FociPy Logo" width="500">
</p>

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Conda](https://img.shields.io/badge/Environment-Conda-green?logo=anaconda&logoColor=white)
![Stage](https://img.shields.io/badge/Stage-Architecture_Design-blue)
![Last Commit](https://img.shields.io/github/last-commit/stanuch/FociPy)
![License](https://img.shields.io/badge/License-MIT-green)
![GitHub repo size](https://img.shields.io/github/repo-size/stanuch/FociPy)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

**FociPy** is a Python pipeline for automated analysis of DNA repair protein recruitment kinetics at laser-induced damage sites. It takes timelapse fluorescence microscopy data from microirradiation experiments, extracts normalized intensity curves, and exports quantitative results ready for publication.

The pipeline is designed around **XRCC1** (single-strand break marker) and **53BP1** (double-strand break marker) accumulation in HeLa cells, but the modular architecture should work for other fluorescently-tagged repair proteins as well.

> **Note:** FociPy is under active development — the modules structure is defined but core algorithms are not yet implemented. This project is part of a master's thesis in Molecular and Cellular Biophysics at the Jagiellonian University (Faculty of Biochemistry, Biophysics and Biotechnology).

## Why?

In microirradiation experiments, a focused 488 nm laser beam induces localized DNA damage inside a single cell nucleus. Fluorescently-tagged repair proteins (e.g. GFP-XRCC1) accumulate at the damage site, forming a visible focus that can be tracked over time.

The standard approach — manual ROI selection in ImageJ/FIJI — is subjective, slow, and doesn't scale well across dozens of cells and conditions. FociPy automates the entire extraction of recruitment kinetics, from raw microscopy files to normalized curves and summary statistics.

The core normalization:

$$I_{norm}(t) = \frac{I_{foci}(t) - I_{bg}}{I_{nuc}(t) - I_{bg}}$$

corrects for variable expression levels (transient transfection) and photobleaching.

## Installation

```bash
# Clone the repository
git clone https://github.com/stanuch/FociPy.git
cd FociPy

# Create conda environment from environment.yml
conda env create -f environment.yml
conda activate focipy

# Install in editable mode
pip install -e .
```

## Experimental context

| Parameter            | Value                                |
| -------------------- | ------------------------------------ |
| **Cell line**        | HeLa (transient transfection)        |
| **Markers**          | RFP-XRCC1 (SSB), GFP-53BP1 (DSB)   |
| **Microscope**       | Leica TCS SP5 FLIM                  |
| **Objective**        | HCX PL APO 63×/1.40 OIL             |
| **Damage induction** | Point microirradiation, 488 nm      |
| **Data format**      | .tif                          |

## Documentation

- [METHODS.md](docs/METHODS.md) — image processing pipeline and algorithms
- [USAGE.md](docs/USAGE.md) — user guide (planned)
- [ROADMAP.md](docs/ROADMAP.md) — development phases and progress
- [CHANGELOG.md](docs/CHANGELOG.md) — version history

## License

[MIT](LICENSE) © 2026 Aleksander Stanuch
