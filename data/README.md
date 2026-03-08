# Data Directory

> Do not commit raw microscopy files to Git — they are too large.
> Use `.gitignore` to exclude them. Consider Zenodo or institutional storage for sharing.

## Structure

```
data/
├── raw/          # Original timelapse files from the microscope (.lif)
└── processed/    # Reserved for any intermediate outputs (not used yet)
```

## Raw Data

<!-- Describe your data here as you start experiments -->
<!-- Expected: Leica .lif timelapse files with DAPI + GFP-XRCC1 channels -->
<!-- Optionally: coordinates.csv with laser hit positions (nucleus_label, x, y) -->

## Naming Convention

<!-- Define your naming convention once you start acquiring data -->
<!-- Example: YYYYMMDD_dose_XX_cellYY.lif -->
