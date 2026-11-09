"""Image I/O, LIF XML metadata parser, and dataset catalog generator for FociPy."""

from __future__ import annotations

import hashlib
import logging
import struct
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)
SUPPORTED_EXTENSIONS = {".lif", ".tif", ".tiff"}
_UNIT_SCALE_M = {"m": 1.0, "mm": 1e-3, "um": 1e-6, "µm": 1e-6, "μm": 1e-6}
_FILETIME_EPOCH = datetime(1601, 1, 1)


@dataclass
class LaserCoordinate:
    """Laser microirradiation point (bleach point) extracted from LIF metadata."""

    name: str
    x_px: float
    y_px: float
    x_m: float
    y_m: float
    duration_ms: float | None = None


@dataclass
class LifSeriesMetadata:
    """Metadata for an image series (or merged FRAP + Pb2/Pb3 series) in a `.lif`."""

    index: int
    name: str
    full_path: str
    parent_name: str | None
    size_x: int
    size_y: int
    size_z: int
    size_t: int
    size_c: int
    pixel_size_x_um: float | None
    pixel_size_y_um: float | None
    frame_times_s: list[float] = field(default_factory=list)
    time_interval_s: float | None = None
    pb2_interval_s: float | None = None
    pre_bleach_frames: int = 0
    expected_frames: int = 0
    laser_coordinates: list[LaserCoordinate] = field(default_factory=list)
    is_snapshot: bool = False
    associated_snapshots: list[str] = field(default_factory=list)
    sub_series_indices: list[int] = field(default_factory=list)
    sub_series_names: list[str] = field(default_factory=list)
    sub_series_frame_counts: list[int] = field(default_factory=list)
    first_timestamp_s: float | None = None
    acquisition_datetime: str | None = None
    zoom: float | None = None
    magnification: float | None = None
    scan_speed_hz: int | None = None
    line_average: int | None = None
    pinhole_airy: float | None = None
    imaging_laser_nm: int | None = None
    imaging_laser_pct: float | None = None
    bleach_laser_nm: int | None = None
    bleach_laser_pct: float | None = None
    emission_band_nm: str | None = None
    detector_gain_v: float | None = None
    bit_depth: int | None = None
    channel_luts: list[str] = field(default_factory=list)

    @property
    def pixel_size_um(self) -> float | None:
        return self.pixel_size_x_um

    @property
    def fov_width_um(self) -> float | None:
        return (
            round(self.size_x * self.pixel_size_x_um, 2)
            if self.pixel_size_x_um
            else None
        )

    @property
    def fov_height_um(self) -> float | None:
        return (
            round(self.size_y * self.pixel_size_y_um, 2)
            if self.pixel_size_y_um
            else None
        )

    @property
    def total_duration_s(self) -> float | None:
        return round(self.frame_times_s[-1], 2) if self.frame_times_s else None

    @property
    def post_bleach_frames(self) -> int:
        return max(0, self.size_t - self.pre_bleach_frames)

    @property
    def n_irradiated_cells(self) -> int:
        return len(self.laser_coordinates)

    @property
    def bleach_duration_ms(self) -> float | None:
        return (
            self.laser_coordinates[0].duration_ms if self.laser_coordinates else None
        )

    @property
    def is_merged(self) -> bool:
        return len(self.sub_series_indices) > 1

    @property
    def is_timelapse(self) -> bool:
        return self.size_t > 1 and not self.is_snapshot

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def extract_lif_xml(path: str | Path) -> str:
    """Read only the UTF-16-LE XML header from a binary Leica `.lif` file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"LIF file not found: {path}")

    with open(path, "rb") as f:
        header = f.read(13)
        if len(header) < 13:
            raise ValueError(f"Invalid .lif file (header too short): {path}")
        magic, _size, test_byte, xml_chars = struct.unpack("<iibi", header)
        if magic != 0x70 or test_byte != 0x2A:
            raise ValueError(f"Invalid .lif header magic bytes in {path.name}")
        return f.read(xml_chars * 2).decode("utf-16-le", errors="replace")


def _parse_dim(dim: dict[str, str]) -> tuple[int, float | None, float]:
    n = int(dim.get("NumberOfElements", 1) or 1)
    scale = _UNIT_SCALE_M.get(dim.get("Unit", "").strip(), 0.0)
    length_m = abs(float(dim.get("Length", 0.0) or 0.0)) * scale
    px_um = round((length_m * 1e6) / n, 6) if (n > 0 and length_m > 0) else None
    return n, px_um, length_m


def _parse_timestamps(
    img_el: ET.Element, size_c: int, size_z: int, size_t: int
) -> tuple[list[float], float | None, float | None, str | None]:
    ts_els = img_el.findall("./TimeStampList/TimeStamp")
    if not ts_els:
        dim4 = img_el.find(
            "./ImageDescription/Dimensions/DimensionDescription[@DimID='4']"
        )
        total_s = float(dim4.attrib.get("Length", 0) or 0) if dim4 is not None else 0.0
        if size_t > 1 and total_s > 0:
            dt = total_s / (size_t - 1)
            return [round(i * dt, 4) for i in range(size_t)], round(dt, 4), None, None
        return [], None, None, None

    raw_s = [
        ((int(t.get("HighInteger", 0)) << 32) | int(t.get("LowInteger", 0))) * 1e-7
        for t in ts_els
    ]
    step = max(1, size_c * size_z)
    abs_t = (
        [raw_s[t * step] for t in range(size_t)]
        if len(raw_s) >= size_t * step and size_t > 0
        else raw_s[:size_t]
    )
    if not abs_t:
        return [], None, None, None

    t0 = abs_t[0]
    acq_dt = (
        (_FILETIME_EPOCH + timedelta(seconds=t0)).strftime("%Y-%m-%d %H:%M:%S")
        if t0 > 1e9
        else None
    )
    frames = [round(t - t0, 4) for t in abs_t]
    dt = round(float(np.median(np.diff(frames))), 4) if len(frames) > 1 else None
    return frames, dt, t0, acq_dt


def _parse_frap(
    img_el: ET.Element, name: str, nx: int, ny: int, lx_m: float, ly_m: float
) -> tuple[int, int, list[LaserCoordinate], int | None, float | None]:
    frap = img_el.find("./Attachment[@Name='ContextDescription']/FRAPplus/Block_FRAP")
    if frap is None:
        return 0, 0, [], None, None

    pre_frames = 0
    expected_frames = 0
    if "pb" not in name.lower():
        seen_bleach = False
        for ti in frap.findall("./Block_FRAP_Time_List/Block_FRAP_Time_Info"):
            if ti.get("IsMinimized") == "219":
                seen_bleach = True
                continue
            fc = int(ti.get("FrameCount", 0) or 0)
            expected_frames += fc
            if not seen_bleach:
                pre_frames += fc

    bleach_nm: int | None = None
    bleach_pct: float | None = None
    bp_info = frap.find("./Block_FRAP_BleachPoint_Info")
    if bp_info is not None:
        for ll in bp_info.findall(".//LaserLineSetting"):
            inten = float(ll.get("IntensityDev", 0) or 0)
            if inten > 0:
                bleach_nm = int(float(ll.get("LaserLine", 0) or 0))
                bleach_pct = round(inten, 2)
                break

    coords: list[LaserCoordinate] = []
    roi_path = (
        "./Block_FRAP_BleachPoint_Info/BleachPointSettingsDefinition"
        "/DCRoiPoints/LMSDataContainerHeader/Element/Children/Element"
    )
    for roi_el in frap.findall(roi_path):
        rs = roi_el.find("./Data/ROISingle")
        tr = rs.find("./Transformation/Translation") if rs is not None else None
        if rs is None or tr is None:
            continue
        vt = rs.find("./Vertices/P")
        x_m = float(tr.get("X", 0)) + (float(vt.get("X", 0)) if vt is not None else 0.0)
        y_m = float(tr.get("Y", 0)) + (float(vt.get("Y", 0)) if vt is not None else 0.0)
        x_px = (nx / 2.0) + (x_m / lx_m) * nx if (lx_m > 0 and nx > 0) else float("nan")
        y_px = (ny / 2.0) + (y_m / ly_m) * ny if (ly_m > 0 and ny > 0) else float("nan")
        att = rs.find("./Attachment[@Name='BLEACH_POINT']")
        dur = (
            float(att.attrib["Duration"])
            if att is not None and "Duration" in att.attrib
            else None
        )
        coords.append(
            LaserCoordinate(
                name=roi_el.get("Name", f"ROI{len(coords) + 1}"),
                x_px=round(x_px, 2),
                y_px=round(y_px, 2),
                x_m=x_m,
                y_m=y_m,
                duration_ms=dur,
            )
        )
    return pre_frames, expected_frames, coords, bleach_nm, bleach_pct


def _parse_hardware(
    img_el: ET.Element, parent_el: ET.Element | None = None
) -> dict[str, Any]:
    hw: dict[str, Any] = {}
    atl = img_el.find(".//ATLConfocalSettingDefinition")
    if atl is None and parent_el is not None:
        atl = parent_el.find("./Data//ATLConfocalSettingDefinition")
        if atl is None:
            atl = parent_el.find("./Attachment//ATLConfocalSettingDefinition")
    if atl is None:
        for rec in img_el.findall(".//ScannerSettingRecord"):
            ident, val = rec.get("Identifier", ""), rec.get("Variant", "")
            if not val:
                continue
            if ident == "dblZoom":
                hw["zoom"] = round(float(val), 2)
            elif ident == "dblPinholeAiry":
                hw["pinhole_airy"] = round(float(val), 2)
            elif ident == "nAverageLine":
                hw["line_average"] = int(float(val))
        return hw

    if atl.get("Zoom"):
        hw["zoom"] = round(float(atl.get("Zoom", 0)), 2)
    if atl.get("Magnification"):
        hw["magnification"] = round(float(atl.get("Magnification", 0)), 1)
    if atl.get("ScanSpeed"):
        hw["scan_speed_hz"] = int(float(atl.get("ScanSpeed", 0)))
    if atl.get("LineAverage"):
        hw["line_average"] = int(float(atl.get("LineAverage", 0)))
    if atl.get("PinholeAiry"):
        hw["pinhole_airy"] = round(float(atl.get("PinholeAiry", 0)), 2)

    active_ch: str | None = None
    for det in atl.findall("./DetectorList/Detector"):
        if det.get("IsActive") == "1" and det.get("Channel", "") != "100":
            active_ch = det.get("Channel")
            if det.get("Gain"):
                hw["detector_gain_v"] = round(float(det.get("Gain", 0)), 1)
            break

    if active_ch:
        mb = atl.find(f".//MultiBand[@Channel='{active_ch}']")
        if mb is not None and mb.get("LeftWorld") and mb.get("RightWorld"):
            left = round(float(mb.get("LeftWorld", 0)))
            right = round(float(mb.get("RightWorld", 0)))
            hw["emission_band_nm"] = f"{left}-{right}"

    for ll in atl.findall("./AotfList/Aotf/LaserLineSetting"):
        inten = float(ll.get("IntensityDev", 0) or 0)
        if inten > 0:
            hw["imaging_laser_nm"] = int(float(ll.get("LaserLine", 0) or 0))
            hw["imaging_laser_pct"] = round(inten, 2)
            break
    return hw


def _merge_frap_group(group: list[LifSeriesMetadata]) -> list[LifSeriesMetadata]:
    """Merge sibling `FRAP Series` and `FRAP Pb2`/`Pb3` series into one series."""
    mains = [s for s in group if "pb" not in s.name.lower()]
    pbs = [s for s in group if "pb" in s.name.lower()]
    if len(mains) != 1 or not pbs:
        return group

    main = mains[0]
    pbs.sort(key=lambda s: (s.first_timestamp_s or float("inf"), s.index))
    for pb in pbs:
        if not pb.frame_times_s and pb.first_timestamp_s is None:
            # Skip unrecorded placeholder Pb2 created when an experiment was aborted
            continue
        if (
            main.first_timestamp_s is not None
            and pb.first_timestamp_s is not None
            and pb.frame_times_s
        ):
            offset_s = pb.first_timestamp_s - main.first_timestamp_s
            pb_rel_times = [round(offset_s + t, 4) for t in pb.frame_times_s]
        elif main.frame_times_s and pb.frame_times_s:
            gap = pb.time_interval_s or main.time_interval_s or 1.0
            start_s = main.frame_times_s[-1] + gap
            pb_rel_times = [round(start_s + t, 4) for t in pb.frame_times_s]
        else:
            pb_rel_times = []

        main.frame_times_s.extend(pb_rel_times)
        main.size_t += pb.size_t
        if main.pb2_interval_s is None and pb.time_interval_s is not None:
            main.pb2_interval_s = pb.time_interval_s
        main.sub_series_indices.extend(pb.sub_series_indices)
        main.sub_series_names.extend(pb.sub_series_names)
        main.sub_series_frame_counts.extend(pb.sub_series_frame_counts)
        for snap in pb.associated_snapshots:
            if snap not in main.associated_snapshots:
                main.associated_snapshots.append(snap)

    return [main]


def parse_lif_metadata(
    path: str | Path,
    exclude_snapshots: bool = True,
    only_timelapse: bool = False,
    merge_pb_series: bool = True,
) -> list[LifSeriesMetadata]:
    """Parse `.lif` XML header into a list of `LifSeriesMetadata`."""
    root = ET.fromstring(extract_lif_xml(path))
    all_series: list[LifSeriesMetadata] = []
    parent_groups: dict[int, list[LifSeriesMetadata]] = {}

    def _walk(
        el: ET.Element, chain: tuple[str, ...], parent_el: ET.Element | None
    ) -> None:
        name = el.get("Name", "")
        cur = (*chain, name) if name else chain
        img = el.find("./Data/Image")
        if img is not None:
            dims = {
                d.get("DimID", ""): d.attrib
                for d in img.findall(
                    "./ImageDescription/Dimensions/DimensionDescription"
                )
            }
            ch_els = img.findall("./ImageDescription/Channels/ChannelDescription")
            sc = max(1, len(ch_els))
            luts = [c.get("LUTName", "") for c in ch_els if c.get("LUTName")]
            bits = (
                int(ch_els[0].get("Resolution", 8) or 8) if ch_els else None
            )
            sx, px_x, lx = _parse_dim(dims.get("1", {}))
            sy, px_y, ly = _parse_dim(dims.get("2", {}))
            sz = int(dims.get("3", {}).get("NumberOfElements", 1) or 1)
            st = int(dims.get("4", {}).get("NumberOfElements", 1) or 1)
            unit_x = dims.get("1", {}).get("Unit", "").strip().lower()
            is_snap = "snapshot" in name.lower() or unit_x == "pixel"
            times, dt, t0, acq_dt = _parse_timestamps(img, sc, sz, st)
            pre, exp_f, coords, bl_nm, bl_pct = _parse_frap(
                img, name, sx, sy, lx, ly
            )
            hw = _parse_hardware(img, parent_el) if not is_snap else {}
            rel = cur[1:] if len(cur) > 1 else cur
            idx = len(all_series)

            meta = LifSeriesMetadata(
                index=idx,
                name=name,
                full_path="/".join(rel),
                parent_name=rel[-2] if len(rel) > 1 else None,
                size_x=sx,
                size_y=sy,
                size_z=sz,
                size_t=st,
                size_c=sc,
                pixel_size_x_um=px_x,
                pixel_size_y_um=px_y,
                frame_times_s=times,
                time_interval_s=dt,
                pre_bleach_frames=pre,
                expected_frames=exp_f,
                laser_coordinates=coords,
                is_snapshot=is_snap,
                sub_series_indices=[idx],
                sub_series_names=[name],
                sub_series_frame_counts=[st],
                first_timestamp_s=t0,
                acquisition_datetime=acq_dt,
                bleach_laser_nm=bl_nm,
                bleach_laser_pct=bl_pct,
                bit_depth=bits,
                channel_luts=luts,
                **hw,
            )
            all_series.append(meta)
            if not is_snap and "frap" in name.lower():
                parent_groups.setdefault(id(parent_el), []).append(meta)

        for child in el.findall("./Children/Element"):
            _walk(child, cur, el)

    for top in root.findall("./Element"):
        _walk(top, (), None)

    pending_snaps: list[str] = []
    last_valid: LifSeriesMetadata | None = None
    for s in all_series:
        if s.is_snapshot:
            pending_snaps.append(s.full_path)
            if last_valid and s.parent_name and s.parent_name == last_valid.parent_name:
                last_valid.associated_snapshots.append(s.full_path)
        else:
            for snap in pending_snaps:
                if snap not in s.associated_snapshots:
                    s.associated_snapshots.append(snap)
            if s.is_timelapse:
                pending_snaps = []
            last_valid = s

    if merge_pb_series:
        removed_ids: set[int] = set()
        for group in parent_groups.values():
            if len(group) > 1:
                kept = _merge_frap_group(group)
                kept_indices = {m.index for m in kept}
                for m in group:
                    if m.index not in kept_indices:
                        removed_ids.add(m.index)
        all_series = [s for s in all_series if s.index not in removed_ids]

    res = [s for s in all_series if not (exclude_snapshots and s.is_snapshot)]
    return [s for s in res if s.is_timelapse] if only_timelapse else res


def load_lif_series(
    path: str | Path,
    series: int | str,
    merge_pb_series: bool = True,
) -> tuple[np.ndarray, LifSeriesMetadata]:
    """Load pixel data `(T, C, Y, X)` and metadata for a series by index or name.

    When `merge_pb_series=True` (default), automatically concatenates `FRAP Series`
    with its sibling `FRAP Pb2 Series` (and `Pb3`) along the time axis `T`.
    """
    from readlif.reader import LifFile

    path = Path(path)
    all_meta = parse_lif_metadata(
        path, exclude_snapshots=False, merge_pb_series=merge_pb_series
    )
    if isinstance(series, str):
        matches = [
            m
            for m in all_meta
            if series in (m.name, m.full_path, m.parent_name)
            or series in m.full_path
            or any(series in sub for sub in m.sub_series_names)
        ]
        if not matches:
            raise KeyError(f"Series '{series}' not found in {path.name}")
        meta = matches[0]
    else:
        matches = [
            m
            for m in all_meta
            if m.index == series or series in m.sub_series_indices
        ]
        if not matches:
            raise IndexError(f"Series index {series} not found in {path.name}")
        meta = matches[0]

    if meta.is_snapshot:
        raise ValueError(
            f"Series '{meta.full_path}' is a Snapshot and cannot be analyzed."
        )

    lif = LifFile(str(path))
    part_arrays: list[np.ndarray] = []
    for sub_idx, sub_t in zip(
        meta.sub_series_indices, meta.sub_series_frame_counts, strict=True
    ):
        lif_img = lif.get_image(sub_idx)
        part = np.stack(
            [
                np.stack(
                    [
                        np.asarray(lif_img.get_frame(z=0, t=t, c=c))
                        for c in range(meta.size_c)
                    ],
                    axis=0,
                )
                for t in range(sub_t)
            ],
            axis=0,
        )
        part_arrays.append(part)

    frames = (
        np.concatenate(part_arrays, axis=0)
        if len(part_arrays) > 1
        else part_arrays[0]
    )
    return frames, meta


def catalog_lif_files(
    root_dir: str | Path,
    output_csv: str | Path | None = None,
    only_timelapse: bool = True,
    merge_pb_series: bool = True,
) -> pd.DataFrame:
    """Scan a directory recursively for `.lif` files and build a rich CSV catalog."""
    import pandas as pd

    root_dir = Path(root_dir)
    if not root_dir.exists():
        raise FileNotFoundError(f"Directory not found: {root_dir}")

    lif_files = (
        [root_dir]
        if root_dir.is_file() and root_dir.suffix.lower() == ".lif"
        else sorted(root_dir.rglob("*.lif"))
    )

    rows: list[dict[str, Any]] = []
    for lif_path in lif_files:
        rel_file = (
            lif_path.relative_to(root_dir)
            if lif_path != root_dir and root_dir in lif_path.parents
            else Path(lif_path.name)
        )
        parts = rel_file.parts
        protein_group = parts[0] if len(parts) > 1 else "root"

        series_list = parse_lif_metadata(
            lif_path,
            exclude_snapshots=True,
            only_timelapse=only_timelapse,
            merge_pb_series=merge_pb_series,
        )

        for s in series_list:
            is_frap = "frap" in s.name.lower() or s.n_irradiated_cells > 0
            if s.size_t <= 1:
                series_type = "z_stack" if s.size_z > 1 else "single_frame"
                status = "static"
            else:
                series_type = "FRAP_timelapse" if is_frap else "timelapse"
                if is_frap and s.post_bleach_frames <= 2:
                    status = "aborted"
                elif is_frap and s.expected_frames > 0 and s.size_t < s.expected_frames:
                    status = "partial"
                else:
                    status = "complete"

            coords_px_str = "; ".join(
                f"{c.name}({c.x_px:.1f},{c.y_px:.1f})" for c in s.laser_coordinates
            )
            exp_date = (
                s.acquisition_datetime[:10]
                if s.acquisition_datetime
                else (parts[1] if len(parts) > 2 else "")
            )

            rows.append(
                {
                    "protein_group": protein_group,
                    "experiment_date": exp_date,
                    "acquisition_datetime": s.acquisition_datetime,
                    "file_name": lif_path.name,
                    "file_path": str(rel_file),
                    "series_index": s.index,
                    "merged_indices": "+".join(
                        str(i) for i in s.sub_series_indices
                    ),
                    "merged_series_names": " + ".join(s.sub_series_names),
                    "experiment_label": s.parent_name or "",
                    "series_name": s.name,
                    "full_path": s.full_path,
                    "series_type": series_type,
                    "status": status,
                    "resolution_xy": f"{s.size_x}x{s.size_y}",
                    "size_x": s.size_x,
                    "size_y": s.size_y,
                    "size_z": s.size_z,
                    "size_c": s.size_c,
                    "total_frames_t": s.size_t,
                    "expected_frames_t": s.expected_frames or s.size_t,
                    "phase_frames": "+".join(
                        str(n) for n in s.sub_series_frame_counts
                    ),
                    "pre_bleach_frames": s.pre_bleach_frames,
                    "post_bleach_frames": s.post_bleach_frames,
                    "pixel_size_um": s.pixel_size_um,
                    "fov_um": (
                        f"{s.fov_width_um:.2f}x{s.fov_height_um:.2f}"
                        if s.fov_width_um and s.fov_height_um
                        else None
                    ),
                    "total_duration_s": s.total_duration_s,
                    "pb1_interval_s": s.time_interval_s,
                    "pb2_interval_s": s.pb2_interval_s,
                    "n_irradiated_cells": s.n_irradiated_cells,
                    "bleach_duration_ms": s.bleach_duration_ms,
                    "laser_coords_px": coords_px_str,
                    "bleach_laser_nm": s.bleach_laser_nm,
                    "bleach_laser_pct": s.bleach_laser_pct,
                    "imaging_laser_nm": s.imaging_laser_nm,
                    "imaging_laser_pct": s.imaging_laser_pct,
                    "emission_band_nm": s.emission_band_nm,
                    "detector_gain_v": s.detector_gain_v,
                    "zoom": s.zoom,
                    "magnification": s.magnification,
                    "pinhole_airy": s.pinhole_airy,
                    "scan_speed_hz": s.scan_speed_hz,
                    "line_average": s.line_average,
                    "bit_depth": s.bit_depth,
                    "channel_luts": "+".join(s.channel_luts),
                    "associated_snapshots_count": len(s.associated_snapshots),
                    "associated_snapshots": "; ".join(s.associated_snapshots),
                }
            )

    df = pd.DataFrame(rows)
    if output_csv is not None:
        out_path = Path(output_csv)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)
        logger.info("Saved LIF series catalog (%d rows) to %s", len(df), out_path)
    return df


def compute_file_hash(path: str | Path, algorithm: str = "sha256") -> str:
    """Compute hex digest hash of a file for audit trail."""
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def load_image(path: Path) -> np.ndarray:
    import tifffile

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported format: '{path.suffix}'")
    return tifffile.imread(str(path))


def save_image(image: np.ndarray, path: Path) -> None:
    import tifffile

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tifffile.imwrite(str(path), image)


def find_images(directory: Path) -> list[Path]:
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory}")
    return sorted(
        p
        for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )
