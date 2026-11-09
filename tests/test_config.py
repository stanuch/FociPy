"""Unit tests for FociPy configuration loading and saving (focipy.config)."""

from pathlib import Path

import pytest

from focipy.config import PipelineConfig


def test_load_default_yaml() -> None:
    """Sprawdza, czy domyślny plik config/default_config.yaml wczytuje się poprawnie."""
    cfg = PipelineConfig.from_yaml()
    assert cfg.laser_wavelength_nm == 488
    assert cfg.kinetics.roi_radius_px == 15
    assert cfg.segmentation.method == "otsu_watershed"


def test_yaml_roundtrip(tmp_path: Path) -> None:
    """Sprawdza zapis konfiguracji do nowego pliku YAML i jej ponowne wczytanie."""
    cfg = PipelineConfig(experiment_name="test_xrcc1_12uJ")
    cfg.kinetics.roi_radius_px = 20

    saved_path = cfg.to_yaml(tmp_path / "custom_config.yaml")
    assert saved_path.exists()

    reloaded = PipelineConfig.from_yaml(saved_path)
    assert reloaded.experiment_name == "test_xrcc1_12uJ"
    assert reloaded.kinetics.roi_radius_px == 20
    assert reloaded.to_dict() == cfg.to_dict()


def test_missing_yaml_raises_error(tmp_path: Path) -> None:
    """Sprawdza, czy brak pliku YAML rzuca czytelny wyjątek FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        PipelineConfig.from_yaml(tmp_path / "nie_istnieje.yaml")
