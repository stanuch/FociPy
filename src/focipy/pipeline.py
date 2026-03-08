"""Main analysis pipeline for FociPy.

Orchestrates the full kinetics workflow:
1. Load timelapse data + metadata
2. Preprocess (noise reduction, background)
3. Segment nuclei (first frame)
4. For each irradiated cell: track ROI, measure intensities, normalize
5. Compute summary statistics
6. Export all results (CSV, JSON, QC images)
"""

# TODO: Implement the following:
# - run_pipeline(input_path, output_dir, config, laser_coordinates) -> Path
# - _ensure_4d(array) -> np.ndarray  (handle 2D/3D/4D input shapes)
