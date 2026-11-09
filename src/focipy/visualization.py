"""Visualization module for FociPy.

Interactive viewing of `.lif` timelapse series in Napari (with fallback to an
interactive Matplotlib slider viewer when Napari is not installed), displaying
multi-channel fluorescence data alongside laser microirradiation target points
and ROI measurement circles.
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Any

import numpy as np

from focipy.io_utils import LifSeriesMetadata, load_lif_series, parse_lif_metadata

logger = logging.getLogger(__name__)


def _phase_label(meta: LifSeriesMetadata, t_idx: int) -> str:
    if t_idx < meta.pre_bleach_frames:
        return "PRE-BLEACH"
    if len(meta.sub_series_frame_counts) > 1:
        pb1_end = meta.sub_series_frame_counts[0]
        if t_idx < pb1_end:
            return "POST-BLEACH (Pb1)"
        return "POST-BLEACH (Pb2)"
    return "POST-BLEACH"


def list_lif_series(
    path: str | Path,
    exclude_snapshots: bool = True,
    only_timelapse: bool = False,
    merge_pb_series: bool = True,
) -> list[LifSeriesMetadata]:
    """Print a summary table of series inside a `.lif` file and return metadata."""
    path = Path(path)
    series_list = parse_lif_metadata(
        path,
        exclude_snapshots=exclude_snapshots,
        only_timelapse=only_timelapse,
        merge_pb_series=merge_pb_series,
    )
    print(f"\n=== {path.name} ({len(series_list)} series) ===")
    print(
        f"{'Idx':>6} | {'Name':<30} | {'Shape (T,C,Y,X)':<17} | "
        f"{'Dur [s]':>7} | {'Pixel [µm]':<10} | {'Pre':>3} | {'Laser ROIs'}"
    )
    print("-" * 104)
    for s in series_list:
        idx_str = "+".join(str(i) for i in s.sub_series_indices)
        shape_str = f"({s.size_t},{s.size_c},{s.size_y},{s.size_x})"
        dur_str = f"{s.total_duration_s:.1f}" if s.total_duration_s else "-"
        px_str = f"{s.pixel_size_um:.4f}" if s.pixel_size_um else "N/A"
        rois_str = (
            ", ".join(
                f"{c.name}({c.x_px:.0f},{c.y_px:.0f})" for c in s.laser_coordinates
            )
            if s.laser_coordinates
            else "-"
        )
        print(
            f"{idx_str:>6} | {s.full_path:<30} | {shape_str:<17} | "
            f"{dur_str:>7} | {px_str:<10} | {s.pre_bleach_frames:>3} | {rois_str}"
        )
    return series_list


def view_in_napari(
    frames: np.ndarray,
    meta: LifSeriesMetadata,
    roi_radius_px: int = 15,
    channel_names: tuple[str, ...] = ("Fluorescence (Protein)", "Transmitted / Ch1"),
    channel_colormaps: tuple[str, ...] = ("magma", "gray"),
    run: bool = True,
) -> Any:
    """Open a loaded `(T, C, Y, X)` series in Napari with laser target overlays.

    Adds each channel as an independent image layer and, if `meta.laser_coordinates`
    are present in the file, overlays:
    - A `Points` layer (`Laser Target (+)`) marking `(y_px, x_px)` hit locations.
    - A `Shapes` layer (`ROI Radius`) showing the circular measurement area.
    """
    try:
        napari: Any = importlib.import_module("napari")
    except ImportError as exc:
        raise ImportError(
            "Napari is not installed in the current environment. "
            'Install it via `pip install "napari[all]"` or use '
            "`view_lif_series(..., backend='matplotlib')`."
        ) from exc

    idx_str = "+".join(str(i) for i in meta.sub_series_indices)
    title = (
        f"FociPy — [{idx_str}] {meta.full_path} "
        f"(px={meta.pixel_size_um or 0:.3f} µm, pre={meta.pre_bleach_frames})"
    )
    viewer = napari.Viewer(title=title)

    n_channels = frames.shape[1]
    for c in range(n_channels):
        ch_name = channel_names[c] if c < len(channel_names) else f"Channel {c}"
        cmap = channel_colormaps[c] if c < len(channel_colormaps) else "gray"
        blending = "additive" if c > 0 else "translucent"
        viewer.add_image(
            frames[:, c, :, :],
            name=ch_name,
            colormap=cmap,
            blending=blending,
        )

    if meta.laser_coordinates:
        # Napari uses (row, col) = (y_px, x_px) for 2D spatial coordinates
        points_yx = np.array(
            [[pt.y_px, pt.x_px] for pt in meta.laser_coordinates], dtype=float
        )
        labels = [
            f"{pt.name} ({pt.duration_ms:.0f} ms)" if pt.duration_ms else pt.name
            for pt in meta.laser_coordinates
        ]

        viewer.add_points(
            points_yx,
            name="Laser Target (+)",
            symbol="cross",
            size=14,
            face_color="lime",
            border_color="lime",
            text={
                "string": labels,
                "color": "lime",
                "translation": np.array([-10, 12]),
            },
        )

        if roi_radius_px > 0:
            circles = [
                np.array([[pt.y_px, pt.x_px], [roi_radius_px, roi_radius_px]])
                for pt in meta.laser_coordinates
            ]
            viewer.add_shapes(
                circles,
                shape_type="ellipse",
                name=f"ROI (r={roi_radius_px} px)",
                edge_color="lime",
                face_color="transparent",
                edge_width=1.5,
            )

    # Update status bar with frame timestamp when scrubbing time slider
    def _update_time_status(event: Any) -> None:
        step = viewer.dims.current_step[0]
        if 0 <= step < len(meta.frame_times_s):
            t_s = meta.frame_times_s[step]
            phase = _phase_label(meta, step)
            viewer.status = (
                f"Frame {step + 1}/{meta.size_t} | t = {t_s:.2f} s ({phase})"
            )

    viewer.dims.events.current_step.connect(_update_time_status)

    if run:
        napari.run()
    return viewer


def view_in_matplotlib(
    frames: np.ndarray,
    meta: LifSeriesMetadata,
    roi_radius_px: int = 15,
    show: bool = True,
) -> Any:
    """Interactive Matplotlib timelapse viewer with a time slider and laser markers."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle
    from matplotlib.widgets import Slider

    n_t, n_c, _ny, _nx = frames.shape
    fig, axes = plt.subplots(1, n_c, figsize=(6 * n_c, 6), squeeze=False)
    plt.subplots_adjust(bottom=0.18, top=0.88)

    cmaps = ["magma", "gray", "viridis", "inferno"]
    im_artists = []

    for c in range(n_c):
        ax = axes[0, c]
        ch_data = frames[:, c]
        vmin = float(np.percentile(ch_data, 1))
        vmax = float(np.percentile(ch_data, 99.8))
        im = ax.imshow(
            frames[0, c],
            cmap=cmaps[c % len(cmaps)],
            vmin=vmin,
            vmax=max(vmax, vmin + 1.0),
        )
        im_artists.append(im)
        ax.set_title(f"Channel {c}")

        for pt in meta.laser_coordinates:
            ax.plot(
                pt.x_px,
                pt.y_px,
                marker="+",
                color="lime",
                markersize=14,
                markeredgewidth=2.0,
                label=pt.name,
            )
            if roi_radius_px > 0:
                ax.add_patch(
                    Circle(
                        (pt.x_px, pt.y_px),
                        radius=roi_radius_px,
                        edgecolor="lime",
                        facecolor="none",
                        linestyle="--",
                        linewidth=1.5,
                    )
                )
            ax.annotate(
                pt.name,
                (pt.x_px, pt.y_px),
                xytext=(6, -6),
                textcoords="offset points",
                color="lime",
                fontsize=9,
                fontweight="bold",
            )

    idx_str = "+".join(str(i) for i in meta.sub_series_indices)

    def _title_for_frame(t_idx: int) -> str:
        t_str = (
            f"t = {meta.frame_times_s[t_idx]:.2f} s"
            if t_idx < len(meta.frame_times_s)
            else f"frame {t_idx}"
        )
        phase = _phase_label(meta, t_idx)
        return (
            f"[{idx_str}] {meta.full_path} | Frame {t_idx + 1}/{n_t} "
            f"({t_str}, {phase}) | px = {meta.pixel_size_um or 0:.3f} µm"
        )

    fig.suptitle(_title_for_frame(0), fontsize=11, fontweight="bold")

    if n_t > 1:
        ax_slider = fig.add_axes((0.15, 0.05, 0.7, 0.04))
        slider = Slider(
            ax=ax_slider,
            label="Frame (T)",
            valmin=0,
            valmax=n_t - 1,
            valinit=0,
            valstep=1,
        )

        def _on_change(val: float) -> None:
            t_idx = int(val)
            for c, im in enumerate(im_artists):
                im.set_data(frames[t_idx, c])
            fig.suptitle(_title_for_frame(t_idx), fontsize=11, fontweight="bold")
            fig.canvas.draw_idle()

        slider.on_changed(_on_change)
        # Keep slider reference alive in figure canvas callback until figure closes
        fig.canvas.mpl_connect("close_event", lambda _evt, _ref=slider: None)

    if show:
        plt.show()
    return fig


def view_lif_series(
    path: str | Path,
    series: int | str | None = None,
    roi_radius_px: int = 15,
    backend: str = "auto",
    merge_pb_series: bool = True,
) -> Any:
    """Load and visualize a series from a `.lif` file with laser target markers.

    Args:
        path: Path to the `.lif` file.
        series: Series index (`int`) or name substring (`str`). If `None`,
            automatically selects the first timelapse series in the file.
        roi_radius_px: Radius of the ROI circle drawn around each laser point.
        backend: `"napari"`, `"matplotlib"`, or `"auto"` (tries Napari first,
            falls back to Matplotlib if Napari is not installed).
        merge_pb_series: Whether to automatically concatenate `FRAP Series` and
            `FRAP Pb2`/`Pb3` series into a single timeline.
    """
    path = Path(path)
    if series is None:
        timelapses = parse_lif_metadata(
            path,
            exclude_snapshots=True,
            only_timelapse=True,
            merge_pb_series=merge_pb_series,
        )
        if not timelapses:
            non_snaps = parse_lif_metadata(
                path, exclude_snapshots=True, merge_pb_series=merge_pb_series
            )
            if not non_snaps:
                raise ValueError(f"No valid non-snapshot series found in {path.name}")
            series = non_snaps[0].index
        else:
            series = timelapses[0].index

    frames, meta = load_lif_series(path, series, merge_pb_series=merge_pb_series)

    if backend == "napari":
        return view_in_napari(frames, meta, roi_radius_px=roi_radius_px)
    if backend == "matplotlib":
        return view_in_matplotlib(frames, meta, roi_radius_px=roi_radius_px)

    if importlib.util.find_spec("napari") is not None:
        return view_in_napari(frames, meta, roi_radius_px=roi_radius_px)
    logger.info("Napari not installed; using Matplotlib interactive viewer.")
    return view_in_matplotlib(frames, meta, roi_radius_px=roi_radius_px)
