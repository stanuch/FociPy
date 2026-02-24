"""Nuclear segmentation module for FociPy.

Provides both classical (Otsu + Watershed) and deep learning (Cellpose)
methods for segmenting cell nuclei from DAPI-stained fluorescence images.
"""

# TODO: Implement the following:
# - OtsuWatershedSegmenter (class)
# - CellposeSegmenter (class)
# - segment_nuclei_otsu(dapi, sigma, min_size, min_distance) -> labeled mask
# - segment_nuclei_cellpose(dapi, diameter) -> labeled mask
# - filter_nuclei_by_size(labeled_mask, min_area, max_area) -> labeled mask
