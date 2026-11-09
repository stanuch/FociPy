"""Unit and integration tests for FociPy LIF metadata parsing and image I/O."""

import struct
from pathlib import Path

import numpy as np
import pytest

from focipy.io_utils import (
    compute_file_hash,
    extract_lif_xml,
    find_images,
    load_image,
    load_lif_series,
    parse_lif_metadata,
    save_image,
)

RAW_12UJ_PATH = Path("data/raw/XRCC1/2026_02_26/2026_02_26 HeLa mRFP-XRCC1 12uJ.lif")


def _build_synthetic_lif_bytes(xml_text: str) -> bytes:
    """Pomocnicza funkcja budująca minimalny binarny nagłówek .lif z podanym XML."""
    xml_bytes = xml_text.encode("utf-16-le")
    xml_chars = len(xml_bytes) // 2
    header = struct.pack("<iibi", 0x70, len(xml_bytes) + 5, 0x2A, xml_chars)
    return header + xml_bytes


def test_parse_synthetic_lif_frap_and_pb2_merge(tmp_path: Path) -> None:
    """Testuje parsowanie XML .lif, punktów BLEACH_POINT i sklejanie FRAP + Pb2."""
    sample_xml = (
        '<?xml version="1.0"?>'
        '<LMSDataContainerHeader Version="2">'
        '<Element Name="Experiment.lif"><Children>'
        '<Element Name="12uJ_cell01"><Children>'
        '<Element Name="FRAP Series01"><Data><Image>'
        "<ImageDescription>"
        "<Channels>"
        '<ChannelDescription LUTName="Yellow" Resolution="8"/>'
        '<ChannelDescription LUTName="Gray" Resolution="8"/>'
        "</Channels>"
        "<Dimensions>"
        '<DimensionDescription DimID="1" NumberOfElements="512" '
        'Length="5.12e-05" Unit="m"/>'
        '<DimensionDescription DimID="2" NumberOfElements="512" '
        'Length="5.12e-05" Unit="m"/>'
        '<DimensionDescription DimID="4" NumberOfElements="5" '
        'Length="40.0" Unit="s"/>'
        "</Dimensions>"
        "</ImageDescription>"
        '<Attachment Name="ContextDescription"><FRAPplus><Block_FRAP>'
        "<Block_FRAP_Time_List>"
        '<Block_FRAP_Time_Info FrameCount="2" IsMinimized="1" Time="10.0"/>'
        '<Block_FRAP_Time_Info FrameCount="1" IsMinimized="219" Time="0.264"/>'
        '<Block_FRAP_Time_Info FrameCount="3" IsMinimized="1" Time="10.0"/>'
        "</Block_FRAP_Time_List>"
        "<Block_FRAP_BleachPoint_Info><BleachPointSettingsDefinition><DCRoiPoints>"
        '<LMSDataContainerHeader><Element Name="DefaultBleachPointROISet"><Children>'
        '<Element Name="ROI1"><Data><ROISingle>'
        '<Vertices><P X="0" Y="0"/></Vertices>'
        '<Transformation><Translation X="5.12e-06" Y="-5.12e-06"/></Transformation>'
        '<Attachment Name="BLEACH_POINT" Duration="264"/>'
        "</ROISingle></Data></Element>"
        "</Children></Element></LMSDataContainerHeader>"
        "</DCRoiPoints></BleachPointSettingsDefinition></Block_FRAP_BleachPoint_Info>"
        "</Block_FRAP></FRAPplus></Attachment>"
        "</Image></Data></Element>"
        '<Element Name="FRAP Pb2 Series02"><Data><Image>'
        "<ImageDescription>"
        "<Channels>"
        '<ChannelDescription LUTName="Yellow" Resolution="8"/>'
        '<ChannelDescription LUTName="Gray" Resolution="8"/>'
        "</Channels>"
        "<Dimensions>"
        '<DimensionDescription DimID="1" NumberOfElements="512" '
        'Length="5.12e-05" Unit="m"/>'
        '<DimensionDescription DimID="2" NumberOfElements="512" '
        'Length="5.12e-05" Unit="m"/>'
        '<DimensionDescription DimID="4" NumberOfElements="3" '
        'Length="60.0" Unit="s"/>'
        "</Dimensions>"
        "</ImageDescription>"
        "</Image></Data></Element>"
        "</Children></Element></Children></Element></LMSDataContainerHeader>"
    )
    lif_file = tmp_path / "synthetic.lif"
    lif_file.write_bytes(_build_synthetic_lif_bytes(sample_xml))

    assert "DefaultBleachPointROISet" in extract_lif_xml(lif_file)

    merged_list = parse_lif_metadata(lif_file, merge_pb_series=True)
    assert len(merged_list) == 1
    meta = merged_list[0]

    # 5 klatek z FRAP Series01 + 3 klatki z FRAP Pb2 Series02 = 8 klatek łącznie
    assert meta.is_merged is True
    assert meta.size_t == 8
    assert meta.pre_bleach_frames == 2
    assert meta.post_bleach_frames == 6
    assert meta.pixel_size_um == pytest.approx(0.1)

    # Przesunięcie +5.12 µm przy polu 51.2 µm (512 px) -> 256 + 51.2 = 307.2 px
    assert len(meta.laser_coordinates) == 1
    roi = meta.laser_coordinates[0]
    assert roi.name == "ROI1"
    assert roi.x_px == pytest.approx(307.2, abs=0.1)
    assert roi.y_px == pytest.approx(204.8, abs=0.1)
    assert roi.duration_ms == 264.0


def test_tiff_io_and_hash(tmp_path: Path) -> None:
    """Sprawdza zapis i odczyt pliku .tif oraz obliczanie sumy kontrolnej SHA-256."""
    arr = np.zeros((4, 2, 32, 32), dtype=np.uint8)
    arr[:, 0, 10:20, 10:20] = 200
    tif_path = tmp_path / "sample.tif"

    save_image(arr, tif_path)
    loaded = load_image(tif_path)

    assert np.array_equal(arr, loaded)
    assert len(compute_file_hash(tif_path)) == 64
    assert find_images(tmp_path) == [tif_path]


@pytest.mark.skipif(
    not RAW_12UJ_PATH.exists(),
    reason="Pominięto test integracyjny: brak pliku surowego w data/raw/",
)
def test_real_lif_file_parsing_and_loading() -> None:
    """Test integracyjny na prawdziwym pliku .lif z eksperymentu XRCC1 12uJ."""
    series_list = parse_lif_metadata(
        RAW_12UJ_PATH, only_timelapse=True, merge_pb_series=True
    )
    assert len(series_list) >= 15

    first = series_list[0]
    # Seria 12uJ_01_02 składa się z 23 klatek (FRAP) + 2 klatek (Pb2) = 25 klatek
    assert first.parent_name == "12uJ_01_02"
    assert first.size_t == 25
    assert first.pre_bleach_frames == 3
    assert len(first.laser_coordinates) == 2

    # Wczytanie pikseli i sprawdzenie kształtu (T, C, Y, X)
    frames, meta = load_lif_series(RAW_12UJ_PATH, series="12uJ_01_02")
    assert frames.shape == (25, 2, 512, 512)
    assert meta.size_t == 25
    for coord in meta.laser_coordinates:
        assert 0 <= coord.x_px < meta.size_x
        assert 0 <= coord.y_px < meta.size_y
