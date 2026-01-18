<p align="center">
  <img src="docs/images/focipy_logo.png" alt="FociPy Logo" width="500">
</p>

**FociPy** is an open-source Python pipeline designed for the automated detection, segmentation, and quantification of protein accumulation at DNA damage sites. While specifically optimized for analyzing XRCC1 foci in response to light-induced DNA damage, the core architecture is modular and can be adapted to various nuclear markers. 

It aims to provide a reproducible and objective alternative to manual foci counting, enabling high-throughput analysis of large microscopy datasets. This software is being developed as part of a **master's thesis** in the field of bioimage analysis and computational biology.

![License](https://img.shields.io/badge/License-MIT-green) 
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=Python)
![Stage](https://img.shields.io/badge/project-very_early_development-red)
![Last Commit](https://img.shields.io/github/last-commit/stanuch/focipy)

> [!WARNING]
> **UNDER DEVELOPMENT - NOT YET USABLE**
> 
> FociPy is currently under active development and is not intended for end users at this stage.
> The software is incomplete, subject to major changes, and the results may be unreliable.
> Do not use this tool for production or quantitative scientific analysis yet.

## Project goals

- Automated segmentation of cell nuclei from fluorescence microscopy images
- Detection and quantification of XRCC1 nuclear foci
- Analysis of XRCC1 accumulation as a function of applied light dose
- Batch processing of large image datasets
- Export of quantitative results for downstream statistical analysis

## Planned features

- Classical and deep-learning-based nuclear segmentation (e.g. Cellpose / StarDist)
- Robust XRCC1 foci detection using image processing methods
- Per-nucleus foci statistics (count, intensity, spatial distribution)
- Fully automated batch analysis pipeline
- Generation of publication-ready plots and tables
- Modular architecture allowing extension to other DNA damage markers

## Current status

- Project stage: **very early development**
- Validation: **not started**
- Documentation: **not started**

The repository currently serves as a development and learning environment. Core algorithms, parameters, and workflows are yet to be defined.

## Disclaimer

This project is a research prototype developed for academic purposes.
I make no guarantees regarding correctness, completeness, or suitability of the results at the current development stage.

**Detailed documentation, including usage instructions (USAGE.md), methodology (METHODS.md), and changelogs (CHANGELOG.md), can be found in the [`docs/`](docs/) directory.**
