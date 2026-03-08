"""Kinetics module for FociPy.

Core module of the project. Responsible for:
- Creating a circular ROI mask around the laser hit point
- Tracking the ROI center-of-mass through a timelapse (drift correction)
- Measuring per-frame fluorescence intensities (I_foci, I_nuc, I_bg)
- Applying the normalization formula: I_norm(t) = (I_foci(t) - I_bg) / (I_nuc(t) - I_bg)
"""

# TODO: Implement the following:
# - create_foci_roi(center_xy, radius, image_shape) -> bool_mask
# - track_foci_center(timelapse, initial_center_xy, radius, nucleus_mask) -> list[(x,y)]
# - compute_roi_drift(centers) -> list[float]
# - measure_intensities(timelapse, roi_centers, roi_radius, nucleus_mask, bg_mask) -> DataFrame
# - normalize_kinetics(df) -> DataFrame (adds I_normalized column)
# - analyze_cell_kinetics(timelapse, center_xy, nucleus_mask, bg_mask, config) -> DataFrame
