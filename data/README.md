# Data Directory

This directory contains microscopy image data used for XRCC1 foci analysis.

## Directory Structure

```
data/
├── raw/        # Original, unprocessed fluorescence microscopy images
└── processed/  # Analysis outputs (segmented nuclei, detected foci, etc.)
```

## Raw Data (`raw/`)

### Expected Format
- **File types**: `.tif`, `.tiff`, `.png`, `.nd2`, or other microscopy formats
- **Channels**: Multi-channel images with separate channels for:
  - DAPI (nuclear stain)
  - XRCC1 (protein of interest)
  - (Optional) Additional markers
- **Bit depth**: 16-bit recommended for fluorescence microscopy

### Naming Convention
Use descriptive filenames that include metadata:
```
[experiment]_[condition]_[replicate]_[timepoint].[ext]

Examples:
- exp001_control_rep1_t0.tif
- exp001_UV_100J_rep1_t30min.tif
- exp002_laser_50mW_rep2_t1h.tif
```

### Metadata
Consider including a `raw/metadata.csv` with:
- Filename
- Experimental condition (dose, treatment, etc.)
- Acquisition date
- Microscope settings (exposure, magnification, etc.)
- Replicate number

## Processed Data (`processed/`)

This directory will contain analysis outputs:
- **Segmentation masks**: `*_nuclei_mask.tif`
- **Foci detections**: `*_foci_mask.tif`
- **Visualizations**: `*_overlay.png`

## Important Notes

> [!WARNING]
> **Do not commit large raw image files to Git!** Use `.gitignore` or consider external data storage (e.g., institutional server, Zenodo, OSF).

> [!TIP]
> For reproducibility, document:
> - Source of images (instrument, lab, collaborator)
> - Preprocessing steps applied before analysis
> - Any manual curation or exclusions
