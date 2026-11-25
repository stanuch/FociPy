"""Unit tests for FociPy configuration loading, saving, and physical unit conversion."""

from pathlib import Path

import pytest

from focipy.config import PipelineConfig, um2_to_px2, um_to_px


def test_load_default_yaml() -> None:
    """Sprawdza, czy domyślny plik config/default_config.yaml wczytuje się poprawnie."""
    cfg = PipelineConfig.from_yaml()
    assert cfg.laser_wavelength_nm == 488
    assert cfg.protein_channel == 0
    assert cfg.transmitted_channel == 1
    assert cfg.segmentation_channel == 0
    assert cfg.kinetics.roi_radius_um == 1.0
    assert cfg.segmentation.method == "li_watershed"
    assert cfg.segmentation.min_nucleus_area_um2 == 40.0


def test_physical_unit_conversions_across_resolutions() -> None:
    """Sprawdza przeliczanie µm -> px dla różnych rozdzielczości (512 vs 1024)."""
    cfg = PipelineConfig.from_yaml()

    # Ten sam fizyczny promień 1.0 µm daje 2× więcej pikseli przy 2× gęstszej siatce
    r_px_512 = cfg.roi_radius_px(pixel_size_um=0.06)
    r_px_1024 = cfg.roi_radius_px(pixel_size_um=0.03)
    assert r_px_512 == pytest.approx(16.6667, abs=1e-3)
    assert r_px_1024 == pytest.approx(2.0 * r_px_512, abs=1e-6)

    # Pole fizyczne 40 µm² przy pikselu 0.1 µm = 4000 px²
    assert um_to_px(2.0, 0.1) == pytest.approx(20.0)
    assert um2_to_px2(40.0, 0.1) == pytest.approx(4000.0)


def test_yaml_roundtrip(tmp_path: Path) -> None:
    """Sprawdza zapis konfiguracji do nowego pliku YAML i jej ponowne wczytanie."""
    cfg = PipelineConfig(experiment_name="test_xrcc1_12uJ")
    cfg.kinetics.roi_radius_um = 1.5
    cfg.segmentation.min_nucleus_area_um2 = 50.0

    saved_path = cfg.to_yaml(tmp_path / "custom_config.yaml")
    assert saved_path.exists()

    reloaded = PipelineConfig.from_yaml(saved_path)
    assert reloaded.experiment_name == "test_xrcc1_12uJ"
    assert reloaded.kinetics.roi_radius_um == 1.5
    assert reloaded.segmentation.min_nucleus_area_um2 == 50.0
    assert reloaded.to_dict() == cfg.to_dict()


def test_missing_yaml_raises_error(tmp_path: Path) -> None:
    """Sprawdza, czy brak pliku YAML rzuca czytelny wyjątek FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        PipelineConfig.from_yaml(tmp_path / "nie_istnieje.yaml")
