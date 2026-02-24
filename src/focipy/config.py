"""Configuration management for FociPy.

Dataclasses for pipeline configuration, loaded from YAML files.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SegmentationConfig:
    """Configuration for nuclear segmentation."""

    method: str = "cellpose"
    # Otsu parameters
    gaussian_sigma: float = 1.5
    min_distance: int = 20
    # Cellpose parameters
    cellpose_model: str = "nuclei"
    cellpose_diameter: float | None = None


@dataclass
class DetectionConfig:
    """Configuration for foci detection."""

    method: str = "dog"
    sigma_low: float = 1.0
    sigma_high: float = 3.0
    threshold: float = 0.05
    min_distance: int = 5


@dataclass
class FilteringConfig:
    """Configuration for nucleus filtering criteria."""

    min_area_um2: float = 30.0
    max_area_um2: float = 300.0
    exclude_border: bool = True
    min_solidity: float = 0.8
    max_eccentricity: float = 0.95


@dataclass
class PipelineConfig:
    """Top-level configuration for the FociPy pipeline."""

    segmentation: SegmentationConfig = field(default_factory=SegmentationConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    filtering: FilteringConfig = field(default_factory=FilteringConfig)
    pixel_size_um: float = 0.325

    @classmethod
    def from_yaml(cls, path: Path) -> "PipelineConfig":
        """Load configuration from a YAML file.

        Args:
            path: Path to the YAML configuration file.

        Returns:
            PipelineConfig instance with values from the file.
        """
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)

        return cls(
            segmentation=SegmentationConfig(
                **data.get("segmentation", {})
            ),
            detection=DetectionConfig(**data.get("detection", {})),
            filtering=FilteringConfig(**data.get("filtering", {})),
            pixel_size_um=data.get("pixel_size_um", 0.325),
        )
