# Development plan for the FociPy project

## Phase 1: Prototyping & Segmentation (Current Stage)
- [x] Repository setup and project structure
- [x] Implement image loading (support for .tif / .czi formats)
- [ ] Test nuclear segmentation algorithms (e.g., Otsu vs. Cellpose comparison)
- [ ] Create basic `segmentation.py` script

## Phase 2: Foci Detection
- [ ] Implement Difference of Gaussians (DoG) algorithm
- [ ] Parameter tuning/calibration on sample data
- [ ] Visualization of detection results (overlaying masks and points on images)

## Phase 3: Quantitative Analysis & Pipeline
- [ ] Count foci within nuclear masks
- [ ] Export results to CSV/Excel files
- [ ] Automate batch processing (full directory iteration)

## Phase 4: Validation & Documentation
- [ ] Compare automated results with manual counting (Ground Truth validation)
- [ ] Generate plots and tables for the thesis
- [ ] Finalize `METHODS.md`
- [ ] Code cleanup and refactoring

## Backlog / Future Improvements
- [ ] GUI (Simple graphical interface, e.g., Streamlit or Napari plugin)
- [ ] Nuclear shape analysis (circularity, area, solidity)