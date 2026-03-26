"""Image I/O utilities for FociPy.

Functions for loading microscopy timelapse data (.lif, .tif, .ome.tif),
extracting experiment metadata (pixel size, time interval, ROI coordinates),
computing file hashes for audit trail, and managing directory structures.
"""

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".lif", ".tif", ".tiff"}

# TODO:
# - load_lif(path) -> (np.ndarray, dict)
# - load_ome_tiff(path) -> (np.ndarray, dict)
# - extract_metadata(path)
# - compute_file_hash(path)
#
# Modify load_image():
# - Return tuple[np.ndarray, dict] instead of just np.ndarray
# - Dispatch to format-specific loaders based on file extension
# - Handle timelapse arrays with shape (T, C, Y, X)


def load_image(path: Path) -> np.ndarray:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported format: '{path.suffix}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    import tifffile

    image = tifffile.imread(str(path))
    logger.info(
        f"Loaded image: {path.name} | shape={image.shape} | dtype={image.dtype}"
    )
    return image


def save_image(image: np.ndarray, path: Path) -> None:
    import tifffile

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tifffile.imwrite(str(path), image)
    logger.info(f"Saved image: {path.name} | shape={image.shape}")


def find_images(directory: Path) -> list[Path]:
    directory = Path(directory)

    if not directory.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory}")

    images = sorted(
        p
        for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    logger.info(f"Found {len(images)} images in {directory.name}/")
    return images
