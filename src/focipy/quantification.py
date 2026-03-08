"""Quantification module for FociPy.

Extracts summary statistics from kinetic curves:
half-time of recruitment (t_half), maximum intensity (I_max),
plateau level, and ROI drift metrics.
"""

# TODO: Implement the following:
# - compute_kinetic_stats(df) -> dict  (I_max, t_max_s, t_half_s, I_plateau, drift stats)
# - aggregate_experiment(cell_stats, cell_ids) -> DataFrame  (one row per cell)
# - _compute_t_half(time_s, i_norm, i_max) -> float  (linear interpolation)
