"""Pipeline configuration for FociPy.

Centralized configuration for all pipeline parameters using physical spatial
units (µm and µm²) so identical settings work across different resolutions
(256×256, 512×512, 1024×1024) and optical zoom levels.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent.parent / "config" / "default_config.yaml"
)


def um_to_px(value_um: float, pixel_size_um: float) -> float:
    """Convert a physical length in micrometers to pixels."""
    if pixel_size_um <= 0:
        raise ValueError(f"pixel_size_um must be positive, got {pixel_size_um}")
    return value_um / pixel_size_um


def um2_to_px2(area_um2: float, pixel_size_um: float) -> float:
    """Convert a physical area in square micrometers to square pixels."""
    if pixel_size_um <= 0:
        raise ValueError(f"pixel_size_um must be positive, got {pixel_size_um}")
    return area_um2 / (pixel_size_um**2)


@dataclass
class SegmentationConfig:
    """Configuration for nuclear and background segmentation (physical units)."""

    method: str = "li_watershed"
    gaussian_sigma_um: float = 0.20
    min_nucleus_area_um2: float = 40.0
    max_nucleus_area_um2: float = 600.0
    min_nucleus_distance_um: float = 5.0
    bg_dilation_um: float = 2.0
    mask_endogenous_foci: bool = True
    endogenous_mad_threshold: float = 3.5


@dataclass
class KineticsConfig:
    """Configuration for ROI tracking and recruitment kinetics extraction."""

    roi_radius_um: float = 1.0
    search_window_um: float = 2.5
    max_local_shift_um: float = 0.8
    snr_track_threshold: float = 2.0
    snr_responder_threshold: float = 2.5
    drift_correction: bool = True
    background_method: str = "dilated_median"


@dataclass
class PreprocessingConfig:
    """Configuration for auxiliary-track image preprocessing and QC."""

    apply_gaussian_aux: bool = True
    gaussian_sigma_um: float = 0.15
    apply_median_aux: bool = False
    saturation_max_fraction: float = 0.01


@dataclass
class OutputConfig:
    """Configuration for pipeline outputs and quality control."""

    export_qc_images: bool = True
    export_kinetics_csv: bool = True
    qc_dpi: int = 150


@dataclass
class PipelineConfig:
    """Master configuration for the FociPy analysis pipeline."""

    experiment_name: str = "default_experiment"
    microscope_model: str = "Leica TCS SP5"
    objective: str = "HCX PL APO 63x/1.40 OIL"
    laser_wavelength_nm: int = 488
    protein_channel: int = 0
    transmitted_channel: int | None = 1
    segmentation_channel: int = 0
    fallback_pixel_size_um: float = 0.0601
    time_interval_s: float | None = None

    segmentation: SegmentationConfig = field(default_factory=SegmentationConfig)
    kinetics: KineticsConfig = field(default_factory=KineticsConfig)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    def resolve_pixel_size_um(self, pixel_size_um: float | None) -> float:
        """Return image pixel size in µm, falling back to `fallback_pixel_size_um`."""
        if pixel_size_um is not None and pixel_size_um > 0:
            return pixel_size_um
        return self.fallback_pixel_size_um

    def roi_radius_px(self, pixel_size_um: float | None = None) -> float:
        """Convert configured `roi_radius_um` to pixels for a given image scale."""
        px_um = self.resolve_pixel_size_um(pixel_size_um)
        return um_to_px(self.kinetics.roi_radius_um, px_um)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to a nested dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PipelineConfig:
        """Create a PipelineConfig instance from a dictionary."""
        if not data:
            return cls()

        data_copy = dict(data)
        seg_data = data_copy.pop("segmentation", {}) or {}
        kin_data = data_copy.pop("kinetics", {}) or {}
        prep_data = data_copy.pop("preprocessing", {}) or {}
        out_data = data_copy.pop("output", {}) or {}

        return cls(
            segmentation=SegmentationConfig(**seg_data),
            kinetics=KineticsConfig(**kin_data),
            preprocessing=PreprocessingConfig(**prep_data),
            output=OutputConfig(**out_data),
            **data_copy,
        )

    @classmethod
    def from_yaml(cls, path: str | Path = DEFAULT_CONFIG_PATH) -> PipelineConfig:
        """Load configuration from a YAML file.

        Args:
            path: Path to the YAML configuration file. Defaults to
                ``config/default_config.yaml``.

        Returns:
            PipelineConfig instance populated with values from the YAML file.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return cls.from_dict(data)

    def to_yaml(self, path: str | Path) -> Path:
        """Save configuration to a YAML file (e.g. alongside analysis results).

        Args:
            path: Destination file path or directory. If a directory is passed,
                saves as ``config.yaml`` inside that directory.

        Returns:
            Path to the written YAML file.
        """
        path = Path(path)
        if path.is_dir() or path.suffix.lower() not in {".yaml", ".yml"}:
            if path.suffix == "":
                path = path / "config.yaml"

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(
                self.to_dict(),
                f,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
            )

        return path
