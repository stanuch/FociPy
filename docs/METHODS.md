# Methodology

> This document will describe the image processing pipeline and algorithms used by FociPy.
> Fill in each section as you implement the corresponding module. Include final parameter values,
> algorithm choices, and references to relevant literature.

## 1. Data Loading & Metadata Extraction

<!-- Module: io_utils.py — describe .lif loading, what metadata you extract, and how -->

## 2. Image Preprocessing

<!-- Module: preprocessing.py — describe which filters you apply and why, with final σ / radius values -->

## 3. Nuclear Segmentation

<!-- Module: segmentation.py — describe Otsu+Watershed pipeline step by step; optionally compare with Cellpose -->

## 4. ROI Tracking & Drift Correction

<!-- Module: kinetics.py — describe how you place the initial ROI, how center-of-mass tracking works -->

## 5. Intensity Measurement & Normalization

<!-- Module: kinetics.py — describe I_foci, I_nuc, I_bg measurement; the normalization formula and its rationale -->

## 6. Quantification Metrics

<!-- Module: quantification.py — define t_half, I_max, I_plateau and how you compute them -->

## 7. Output & Reproducibility

<!-- Module: reporting.py — describe what files are exported and how reproducibility is ensured (hashes, config) -->

## 8. Libraries & Environment

<!-- List final library versions used in analysis -->
