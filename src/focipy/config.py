"""Pipeline configuration for FociPy.

Centralized configuration for all pipeline parameters.
Uses Python dataclasses with YAML loading/saving support,
so every analysis run is fully reproducible.
"""

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent.parent / "config" / "default_config.yaml"
)


@dataclass
class SegmentationConfig:
    """Configuration for nuclear segmentation."""

    method: str = "otsu_watershed"
    gaussian_sigma: float = 2.0
    min_area_px: int = 500
    max_area_px: int = 50000


@dataclass
class KineticsConfig:
    """Configuration for ROI tracking and recruitment kinetics extraction."""

    roi_radius_px: int = 15
    drift_correction: bool = True
    background_method: str = "outside_nuclei"


@dataclass
class PreprocessingConfig:
    """Configuration for image preprocessing."""

    apply_gaussian: bool = True
    gaussian_sigma: float = 1.0
    apply_median: bool = False


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
    microscope_model: str = "Leica TCS SP5 FLIM"
    objective: str = "HCX PL APO 63x/1.40 OIL"
    laser_wavelength_nm: int = 488
    dapi_channel: int = 0
    protein_channel: int = 1
    time_interval_s: float | None = None

    segmentation: SegmentationConfig = field(default_factory=SegmentationConfig)
    kinetics: KineticsConfig = field(default_factory=KineticsConfig)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to a nested dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PipelineConfig":
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
    def from_yaml(cls, path: str | Path = DEFAULT_CONFIG_PATH) -> "PipelineConfig":
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
