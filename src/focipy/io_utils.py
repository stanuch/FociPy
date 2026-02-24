"""Image I/O utilities for FociPy.

Functions for loading and saving microscopy images,
parsing experiment metadata from filenames, and
managing directory structures.
"""

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

# Supported microscopy image formats
SUPPORTED_EXTENSIONS = {".tif", ".tiff", ".png", ".czi", ".nd2"}


def load_image(path: Path) -> np.ndarray:
    """Load a microscopy image from disk.

    Supports TIFF files via tifffile. For vendor-specific formats
    (.czi, .nd2), consider using aicsimageio.

    Args:
        path: Path to the image file.

    Returns:
        Image as a numpy array. For multi-channel images,
        shape is typically (C, Y, X).

    Raises:
        FileNotFoundError: If the image file doesn't exist.
        ValueError: If the file format is not supported.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported format: '{path.suffix}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # Use tifffile for TIFF, cv2 as fallback for PNG
    import tifffile

    image = tifffile.imread(str(path))
    logger.info(
        f"Loaded image: {path.name} | shape={image.shape} | dtype={image.dtype}"
    )
    return image


def save_image(image: np.ndarray, path: Path) -> None:
    """Save an image to disk.

    Args:
        image: Image array to save.
        path: Output file path. Parent directories will be created if needed.
    """
    import tifffile

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tifffile.imwrite(str(path), image)
    logger.info(f"Saved image: {path.name} | shape={image.shape}")


def find_images(directory: Path) -> list[Path]:
    """Find all supported image files in a directory (non-recursive).

    Args:
        directory: Directory to search.

    Returns:
        Sorted list of image file paths.

    Raises:
        FileNotFoundError: If the directory doesn't exist.
    """
    directory = Path(directory)

    if not directory.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory}")

    images = sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    logger.info(f"Found {len(images)} images in {directory.name}/")
    return images
