# Methodology

> This document describes the image processing pipeline, metadata extraction algorithms,
> coordinate transformations, and reproducibility mechanisms implemented in **FociPy**.

## 1. Data Loading & Metadata Extraction

### 1.1 Fast Binary `.lif` XML Header Parsing
Leica Application Suite Advanced Fluorescence (LAS AF) `.lif` files store both experiment metadata and raw multi-dimensional image buffers in a single binary container that can exceed several hundred megabytes. To inspect or catalog files without reading pixel blocks into memory, `focipy.io_utils.extract_lif_xml()` parses only the binary header prefix:

1. Reads the first 13 bytes using little-endian structure `<iibi`:
   - `magic` (`int32`): validated against `0x70` (`112`),
   - `chunk_size` (`int32`),
   - `test_byte` (`uint8`): validated against `0x2A` (`42`),
   - `xml_chars` (`int32`): number of UTF-16-LE characters in the XML header.
2. Reads exactly `xml_chars * 2` bytes and decodes them as `utf-16-le`.

This reduces metadata extraction time to ~2–15 ms per `.lif` file regardless of total file size.

### 1.2 Spatial Calibration & Dimensions
For each `<Element>` containing `<Data><Image>`, spatial and temporal dimensions are extracted from `<DimensionDescription>` tags:
- `DimID="1"` ($X$), `DimID="2"` ($Y$), `DimID="3"` ($Z$), `DimID="4"` ($T$).
- Given `NumberOfElements` ($N_x, N_y$) and physical field-of-view length `Length` ($L_x, L_y$, converted to meters via unit scale), the calibrated pixel size in micrometers is:

$$\Delta x = \frac{|L_x| \cdot 10^6}{N_x}, \qquad \Delta y = \frac{|L_y| \cdot 10^6}{N_y}$$

### 1.3 Frame Timestamps & Acquisition Clock
Frame acquisition timestamps are stored in `<TimeStampList><TimeStamp>` as 64-bit Windows `FILETIME` integers (`HighInteger`, `LowInteger`), representing 100-nanosecond ticks elapsed since `1601-01-01 00:00:00 UTC`:

$$t_{\text{abs}, k} = \bigl((\text{HighInteger}_k \ll 32) \;\mid\; \text{LowInteger}_k\bigr) \times 10^{-7}\;\text{s}$$

Because Leica records a timestamp for every channel and Z-slice, FociPy strides the timestamp list by $\text{step} = \max(1, N_C \times N_Z)$ to obtain the primary timestamp of each time frame $t \in \{0, \dots, N_T - 1\}$. Relative frame times are computed as $t_k = t_{\text{abs}, k} - t_{\text{abs}, 0}$, and $t_{\text{abs}, 0}$ is converted to an ISO calendar timestamp (`acquisition_datetime`).

### 1.4 Multi-Phase FRAP Series Concatenation (`FRAP Series` + `Pb2` / `Pb3`)
In the Leica LAS AF FRAP Wizard, protocols with multiple post-bleach sampling rates (e.g., fast sampling every `10.48 s` in Post-bleach 1 followed by slow sampling every `30.0 s` in Post-bleach 2) are split across sibling XML `<Element>` nodes under the same experiment container:
- **`FRAP SeriesXX`**: contains the **Pre-bleach** frames and **Post-bleach 1 (`Pb1`)** frames.
- **`FRAP Pb2 SeriesYY`** (and optionally **`FRAP Pb3 SeriesZZ`**): contains the subsequent **Post-bleach 2** (and **3**) frames of the exact same cell(s).

When `merge_pb_series=True` (default):
1. Sibling FRAP series within the same parent XML `<Element>` are grouped and ordered by their absolute start timestamp $t_{\text{abs}, 0}$.
2. If an experiment was aborted during `Pb1`, Leica creates an unrecorded `FRAP Pb2` placeholder (`size_t = 1`, zero `<TimeStamp>` entries). FociPy detects the missing timestamps and discards the empty placeholder.
3. For valid `Pb2`/`Pb3` series, relative timestamps are shifted onto the primary series timeline:

$$t_{k}^{(\text{merged})} = \bigl(t_{\text{abs}, 0}^{(\text{Pb2})} - t_{\text{abs}, 0}^{(\text{main})}\bigr) + t_k^{(\text{Pb2})}$$

4. During image loading (`load_lif_series`), the 4D frame arrays `(T_i, C, Y, X)` of all constituent sub-series (`sub_series_indices`) are concatenated along axis `0` (`T`).

### 1.5 Laser Microirradiation Coordinates & Pre-Bleach Frames
From `<Attachment Name="ContextDescription"><FRAPplus><Block_FRAP>`:
- **Pre-bleach and expected frame counts**: `<Block_FRAP_Time_Info>` elements precede (`pre_bleach_frames`) and follow the bleach pulse marker (`IsMinimized="219"`). Summing `FrameCount` across all non-bleach phases yields `expected_frames`, enabling automatic classification of series into `complete`, `partial`, or `aborted` ($\le 2$ post-bleach frames).
- **Laser target coordinates**: Each irradiated point `<ROISingle>` inside `<Block_FRAP_BleachPoint_Info>` stores physical coordinates in meters relative to the center of the field of view (`Translation` + `Vertices/P`). FociPy converts physical offsets $(x_{\text{m}}, y_{\text{m}})$ into image pixel coordinates $(x_{\text{px}}, y_{\text{px}})$:

$$x_{\text{px}} = \frac{N_x}{2} + \frac{x_{\text{m}}}{L_x} N_x, \qquad y_{\text{px}} = \frac{N_y}{2} + \frac{y_{\text{m}}}{L_y} N_y$$

- **Bleach duration & laser settings**: Pulse duration (in ms) is read from `<Attachment Name="BLEACH_POINT" Duration="..."/>`, while active bleach and imaging laser wavelengths (`nm`) and AOTF power percentages (`%`) are extracted from `<LaserLineSetting>` records where `IntensityDev > 0`.

### 1.6 Snapshot Filtering
LAS AF overview screenshots (`*Snapshot*`) have uncalibrated pixel units (`Unit="pixel"`, `size_t = 1`) and often contain burned-in UI overlays (green crosshairs or multi-panel views). FociPy flags these with `is_snapshot=True`, excludes them from analysis by default (`exclude_snapshots=True`), and records their paths in the parent timelapse series' `associated_snapshots` list for reference.

---

## 2. Image Preprocessing

*(Planned — background estimation and optional Gaussian smoothing configured via `PreprocessingConfig`.)*

---

## 3. Nuclear Segmentation

*(Planned — Cellpose and Otsu thresholding configured via `SegmentationConfig`.)*

---

## 4. ROI Tracking & Drift Correction

*(Planned — phase cross-correlation registration and circular ROI masks centered at `LaserCoordinate` targets configured via `KineticsConfig`.)*

---

## 5. Intensity Measurement & Normalization

Double-normalization of foci intensity against whole-nucleus fluorescence and background:

$$I_{\text{norm}}(t) = \frac{I_{\text{foci}}(t) - I_{\text{bg}}(t)}{I_{\text{nuc}}(t) - I_{\text{bg}}(t)}$$

*(Implementation in `kinetics.py` in progress.)*

---

## 6. Quantification Metrics

*(Planned — recruitment half-time $t_{1/2}$, maximum amplitude $I_{\max}$, and plateau intensity $I_{\text{plateau}}$ in `quantification.py`.)*

---

## 7. Output & Reproducibility

### 7.1 Centralized Configuration & Provenance (`config.py`)
All analysis parameters are encapsulated in `PipelineConfig` (composed of `SegmentationConfig`, `KineticsConfig`, `PreprocessingConfig`, and `OutputConfig`) backed by `config/default_config.yaml`. Every pipeline run serializes a timestamped copy of the active `PipelineConfig` (`cfg.to_yaml(output_dir / "config_used.yaml")`) alongside output tables and figures, ensuring full parameter provenance. Input file integrity can be verified via SHA-256 digests (`compute_file_hash`).

### 7.2 Dataset Inventory Cataloging (`catalog_lif_files`)
`focipy.io_utils.catalog_lif_files()` recursively scans raw data directories (`data/raw`) and compiles a 38-column CSV table (`data/processed/raw_series_catalog.csv`) capturing protein group, acquisition date/time, merged series indices, dimensions, frame counts per phase, pixel size, field of view, phase intervals (`pb1_interval_s`, `pb2_interval_s`), number of irradiated cells, laser coordinates, bleach duration, laser wavelengths/powers, PMT detector gain, emission band, zoom, and protocol completion status.

---

## 8. Libraries & Environment

| Package | Role |
| :--- | :--- |
| **Python >= 3.11** | Core language runtime (`dataclasses`, structural typing) |
| **NumPy / SciPy / Pandas** | N-dimensional array manipulation, signal processing, tabular export |
| **readlif / tifffile** | Leica `.lif` frame decoding and TIFF I/O |
| **xml.etree.ElementTree / struct** | Direct binary `.lif` header unpacking and XML metadata parsing |
| **Napari / Matplotlib** | Interactive multi-channel timelapse visualization and ROI overlays |
| **PyYAML** | Human-readable configuration loading and provenance serialization |
| **Ruff / Pytest** | Static analysis, formatting, and automated unit testing |
