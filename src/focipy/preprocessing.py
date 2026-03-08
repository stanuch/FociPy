"""Image preprocessing module for FociPy.

Functions for intensity normalization, noise reduction,
and background subtraction of fluorescence microscopy images.
"""

# TODO: Implement the following:
# - apply_gaussian(image, sigma) -> np.ndarray
# - apply_median(image, size) -> np.ndarray
# - subtract_background(image, radius) -> np.ndarray  (white top-hat transform)
# - clip_intensity_percentile(image, low, high) -> np.ndarray
# - preprocess_frame(image, config) -> np.ndarray  (chains all steps based on config)
# - preprocess_timelapse(timelapse, channel, config) -> np.ndarray  (applies per frame)
