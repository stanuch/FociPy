# FociPy User Guide

This guide covers installation, dataset cataloging, interactive `.lif` inspection and visualization, and configuration management in **FociPy**.

---

## 1. Installation

Clone the repository and create the Conda environment:

```bash
git clone https://github.com/stanuch/FociPy.git
cd FociPy

conda env create -f environment.yml
conda activate focipy

# Install FociPy in editable mode
pip install -e .
```

To enable the **Napari** desktop viewer (optional; FociPy automatically falls back to an interactive Matplotlib viewer if Napari is not installed):

```bash
pip install -e ".[napari]"
```

---

## 2. Command-Line Interface Overview

FociPy provides the `focipy` command-line tool (also callable via `python -m focipy`):

```bash
focipy help               # Show general manual, options, and examples
focipy help <command>     # Show detailed options for info, view, or catalog
focipy --version          # Show installed FociPy version
```

---

## 3. Data Preparation & Dataset Cataloging (`focipy catalog`)

Place raw Leica `.lif` files under `data/raw/` (for example grouped by protein and experiment date, such as `data/raw/XRCC1/2026_02_26/*.lif` and `data/raw/53BP1/2026_06_11/*.lif`).

To scan the entire `data/raw/` directory and generate a comprehensive CSV summary table of all timelapse series:

```bash
focipy catalog data/raw -o data/processed/raw_series_catalog.csv
```

### Options
- `dir` — Root directory (or single `.lif` file) to scan recursively (default: `data/raw`).
- `-o, --output FILE` — Path to the output CSV file (default: `data/processed/raw_series_catalog.csv`).
- `--include-static` — Include single-frame static preview images (`T = 1`) in addition to multi-frame timelapses.
- `--no-merge` — Keep `FRAP Series` and `FRAP Pb2`/`Pb3` post-bleach phases as separate rows instead of merging them.

### Key Columns in `raw_series_catalog.csv`
- `protein_group`, `experiment_date`, `acquisition_datetime`, `file_name`, `full_path`
- `series_index`, `merged_indices` (e.g. `4+5`), `phase_frames` (e.g. `23+2`)
- `series_type` (`FRAP_timelapse`, `timelapse`) and `status`:
  - `complete` — full planned FRAP protocol acquired,
  - `partial` — stopped earlier during the slow post-bleach phase, but usable for kinetics,
  - `aborted` — stopped immediately after the laser shot ($\le 2$ post-bleach frames).
- `resolution_xy`, `total_frames_t`, `expected_frames_t`, `pre_bleach_frames`, `post_bleach_frames`
- `pixel_size_um`, `fov_um`, `total_duration_s`, `pb1_interval_s`, `pb2_interval_s`
- `n_irradiated_cells`, `bleach_duration_ms`, `laser_coords_px`
- `bleach_laser_nm`, `bleach_laser_pct`, `imaging_laser_nm`, `imaging_laser_pct`, `emission_band_nm`, `detector_gain_v`, `zoom`, `magnification`, `pinhole_airy`, `scan_speed_hz`, `line_average`

---

## 4. Inspecting & Visualizing `.lif` Files (`focipy info` & `focipy view`)

### 4.1 Listing Series in a `.lif` File (`focipy info`)

```bash
# List all non-snapshot series (with FRAP + Pb2 automatically merged)
focipy info "data/raw/XRCC1/2026_02_26/2026_02_26 HeLa mRFP-XRCC1 25uJ.lif"

# Show only multi-frame timelapse series
focipy info "data/raw/53BP1/2026_05_06/20260506_mCH-53BP1 HeLa.lif" --timelapse-only

# Inspect raw unmerged sub-series and include Snapshot screenshots
focipy info "data/raw/XRCC1/2026_02_26/2026_02_26 HeLa mRFP-XRCC1 25uJ.lif" \
    --no-merge --include-snapshots
```

### 4.2 Interactive Visualization (`focipy view`)

`focipy view` loads the `(T, C, Y, X)` timelapse series (concatenating `FRAP Series` and `FRAP Pb2`/`Pb3` automatically) and overlays:
- Green crosshairs (`+`) at every laser microirradiation point (`ROI1..N`),
- Dashed circular ROI boundaries (`roi_radius_px` from config),
- Real-time frame timestamp $t$ and protocol phase (`PRE-BLEACH`, `POST-BLEACH (Pb1)`, `POST-BLEACH (Pb2)`).

```bash
# View series by index (uses Napari if installed, otherwise Matplotlib slider)
focipy view "data/raw/XRCC1/2026_02_26/2026_02_26 HeLa mRFP-XRCC1 25uJ.lif" -s 4

# View series by experiment folder name or substring
focipy view "data/raw/XRCC1/2026_02_26/2026_02_26 HeLa mRFP-XRCC1 12uJ.lif" -s "12uJ_05"

# Force Matplotlib backend and use a custom config YAML for ROI radius
focipy view "data/raw/53BP1/2026_05_06/20260506_mCH-53BP1 HeLa.lif" \
    -s 2 --backend matplotlib -c config/default_config.yaml
```

### 4.3 Python API

```python
from focipy.io_utils import catalog_lif_files, load_lif_series, parse_lif_metadata
from focipy.visualization import view_lif_series

lif_path = "data/raw/XRCC1/2026_02_26/2026_02_26 HeLa mRFP-XRCC1 25uJ.lif"

# 1. Fast XML metadata parsing (~5 ms, no pixel data loaded)
series_meta = parse_lif_metadata(lif_path, only_timelapse=True)
for s in series_meta:
    print(s.index, s.full_path, s.size_t, s.pixel_size_um, s.laser_coordinates)

# 2. Load concatenated (T, C, Y, X) pixel array and metadata
frames, meta = load_lif_series(lif_path, series="25uJ_01")
print(frames.shape, meta.total_duration_s)

# 3. Open interactive viewer
view_lif_series(lif_path, series=4, roi_radius_px=15)
```

---

## 5. Configuration (`PipelineConfig`)

All analysis parameters live in [`config/default_config.yaml`](../config/default_config.yaml) and are represented in Python by `focipy.config.PipelineConfig`:

```python
from focipy.config import PipelineConfig

# Load default configuration (config/default_config.yaml)
cfg = PipelineConfig.from_yaml()

# Override parameters for a specific experiment and save provenance copy
cfg.kinetics.roi_radius_px = 12
cfg.to_yaml("data/processed/run_01/config_used.yaml")
```

---

## 6. Troubleshooting

- **Napari is not installed**: `focipy view` automatically falls back to the interactive Matplotlib slider viewer. You can also pass `--backend matplotlib` explicitly, or install Napari with `pip install "napari[all]"`.
- **`ValueError: Series '...' is a Snapshot`**: Leica `*Snapshot*` entries are single-frame RGB screenshots with burned-in UI markers rather than raw quantitative fluorescence data. Select the corresponding `FRAP Series` timelapse instead.
- **Why does `focipy info` show indices like `4+5`?**: Leica LAS AF saves the fast (`Pb1`) and slow (`Pb2`) post-bleach phases of a single FRAP measurement as separate child series. FociPy merges them into one continuous timeline by default; pass `--no-merge` if you wish to inspect them separately.
