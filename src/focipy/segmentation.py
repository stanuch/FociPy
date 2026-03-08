"""Nuclear segmentation module for FociPy.

Provides both classical (Otsu + Watershed) and deep learning (Cellpose)
methods for segmenting cell nuclei from DAPI-stained fluorescence images.
"""

# TODO: Implement the following:
# - segment_nuclei(image, config) -> labeled_mask  (dispatcher: calls otsu or cellpose)
# - segment_nuclei_otsu(image, sigma, min_area, max_area, min_distance) -> labeled_mask
# - segment_nuclei_cellpose(image, diameter, model_type) -> labeled_mask
# - filter_nuclei_by_area(labeled_mask, min_area, max_area) -> labeled_mask
# - get_background_mask(labeled_mask) -> bool_mask  (all pixels outside nuclei, for I_bg)
