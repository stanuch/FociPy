# FociPy – XRCC1 Foci Analyzer

> [!WARNING]
> **UNDER DEVELOPMENT - NOT YET USABLE**
>  
> FociPy is currently under active development and is not intended for end users at this stage.
> The software is incomplete, subject to major changes, and the results may be unreliable.
> Do not use this tool for production or quantitative scientific analysis yet.

## Overview

**FociPy** is a Python-based pipeline for automated detection and quantification of XRCC1 DNA damage foci in cell nuclei from fluorescence microscopy images.

The project focuses on image-based analysis of protein accumulation in response to light-induced DNA damage. It aims to provide a reproducible and objective alternative to manual foci counting, enabling high-throughput analysis of large microscopy datasets.

This software is being developed as part of a **master's thesis** in the field of bioimage analysis and computational biology.

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

The repository currently serves as a development and learning environment. Core algorithms, parameters, and workflows are subject to change.

## Technologies (planned)

- Python 3
- NumPy, SciPy
- scikit-image, OpenCV
- pandas, matplotlib
- Cellpose / StarDist (optional, for nuclear segmentation)

## Repository structure (planned)

```text
focipy/
│
├── data/            # Raw and processed microscopy images
│   ├── processed/   # Processed microscopy images
│   └── raw/         # Raw microscopy images
│
├── src/             # Core analysis pipeline
│   ├── segmentation.py
│   ├── foci_detection.py
│   └── analysis.py
│
├── notebooks/       # Exploratory data analysis and parameter tuning
├── results/         # Output tables and plots
├── requirements.txt
└── README.md
```

## Disclaimer

This project is a research prototype developed for academic purposes.
The author makes no guarantees regarding correctness, completeness, or suitability of the results at the current development stage.