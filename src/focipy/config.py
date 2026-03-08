"""Pipeline configuration for FociPy.

Centralized configuration for all pipeline parameters.
Uses Python dataclasses with YAML loading/saving support,
so every analysis run is fully reproducible.
"""

# TODO: Implement the following:
# - SegmentationConfig (dataclass): method, gaussian_sigma, min_area_px, max_area_px
# - KineticsConfig (dataclass): roi_radius_px, drift_correction, background_method
# - PreprocessingConfig (dataclass): apply_gaussian, gaussian_sigma, apply_median
# - OutputConfig (dataclass): export_qc_images, export_kinetics_csv, qc_dpi
# - PipelineConfig (master dataclass): experiment_name, channels, sub-configs
#   - from_yaml(path) -> PipelineConfig
#   - to_yaml(path)
#   - to_dict() -> dict
