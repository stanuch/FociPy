# Development Roadmap

> Track progress here. Mark items with [x] as you complete them.

## Phase 1: Architecture & Setup ✅

- [x] Project structure, module stubs, pyproject.toml
- [x] Documentation templates

## Phase 2: Core Implementation

- [ ] `config.py`
- [ ] `io_utils.py` — .lif support, metadata
- [ ] `preprocessing.py`
- [ ] `segmentation.py`

## Phase 3: Kinetics Pipeline

- [ ] `kinetics.py` — ROI tracking, normalization
- [ ] `quantification.py` — t_half, I_max
- [ ] Test on real data

## Phase 4: Output & Visualization

- [ ] `reporting.py`, `visualization.py`
- [ ] `pipeline.py`, `__main__.py` (CLI)

## Phase 5: Validation & Thesis

- [ ] Compare with manual analysis (ImageJ/FIJI)
- [ ] Dose-response experiments
- [ ] Thesis plots and tables

## Backlog

- [ ] Cellpose vs Otsu comparison
- [ ] Photobleaching correction
- [ ] Batch processing
- [ ] GUI / Napari plugin
