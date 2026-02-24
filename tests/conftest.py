"""Shared test fixtures for FociPy tests."""

import numpy as np
import pytest


@pytest.fixture
def synthetic_nuclei_image() -> np.ndarray:
    """Create a 256x256 uint16 image with 3 circular 'nuclei'.

    Nuclei are bright circles on a dark background,
    simulating a DAPI-stained fluorescence image.
    """
    img = np.zeros((256, 256), dtype=np.uint16)
    yy, xx = np.ogrid[:256, :256]

    for cx, cy, radius in [(64, 64, 25), (192, 64, 30), (128, 192, 20)]:
        mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius ** 2
        img[mask] = 10000

    return img


@pytest.fixture
def synthetic_foci_image() -> np.ndarray:
    """Create a 256x256 float64 image with 5 Gaussian 'foci'.

    Foci are small bright spots simulating XRCC1 accumulation.
    """
    img = np.zeros((256, 256), dtype=np.float64)
    yy, xx = np.ogrid[:256, :256]

    for cx, cy in [(50, 50), (100, 100), (150, 150), (200, 200), (64, 192)]:
        img += 1000.0 * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * 3 ** 2))

    return img


@pytest.fixture
def tmp_image(tmp_path, synthetic_nuclei_image) -> "Path":
    """Save a synthetic nuclei image to a temporary TIFF file."""
    import tifffile
    from pathlib import Path

    path = tmp_path / "test_image.tif"
    tifffile.imwrite(str(path), synthetic_nuclei_image)
    return path
