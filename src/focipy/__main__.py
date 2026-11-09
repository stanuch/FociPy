"""Command-line interface for FociPy."""

from __future__ import annotations

import argparse
from pathlib import Path

from focipy import __version__
from focipy.config import PipelineConfig
from focipy.io_utils import catalog_lif_files
from focipy.visualization import list_lif_series, view_lif_series

HELP_OVERVIEW = f"""\
focipy v{__version__} — DNA repair protein recruitment kinetics at laser-damage sites

USAGE
  focipy <command> [options] [arguments]

COMMANDS
  info       Inspect series metadata, dimensions, and laser ROIs in a .lif file
  view       Launch interactive timelapse viewer (Napari or Matplotlib)
  catalog    Scan a directory of .lif files and export a metadata table (.csv)
  help       Show this help message or detailed help for a specific command

GLOBAL OPTIONS
  -h, --help                 Show this help message and exit
  -V, --version              Show program version and exit

COMMAND OPTIONS
  focipy info <file.lif>
    --timelapse-only         List only multi-frame timelapse series (T > 1)
    --include-snapshots      Include screenshot (Snapshot) series in the table
    --no-merge               Do not merge FRAP Series with FRAP Pb2/Pb3 phases

  focipy view <file.lif>
    -s, --series SERIES      Series index (e.g. 4) or name (e.g. '25uJ_01')
    -c, --config FILE        YAML config path (reads kinetics.roi_radius_px)
    --backend BACKEND        Viewer backend: auto, napari, matplotlib [auto]
    --no-merge               Do not merge FRAP Series with FRAP Pb2/Pb3 phases

  focipy catalog [dir]
    -o, --output FILE        Output CSV path [data/processed/raw_series_catalog.csv]
    --include-static         Include single-frame static images (T = 1)
    --no-merge               Keep FRAP Series and Pb2/Pb3 as separate rows

EXAMPLES
  # List merged FRAP series, frame counts, pixel sizes, and laser ROI coordinates
  focipy info "data/raw/XRCC1/2026_02_26/2026_02_26 HeLa mRFP-XRCC1 25uJ.lif"

  # View series 4 in Napari (or Matplotlib fallback) with laser crosshair and ROI circle
  focipy view "data/raw/XRCC1/2026_02_26/2026_02_26 HeLa mRFP-XRCC1 25uJ.lif" -s 4

  # View a series by experiment label using the Matplotlib slider interface
  focipy view "data/raw/XRCC1/2026_02_26/2026_02_26 HeLa mRFP-XRCC1 12uJ.lif" \\
      -s "12uJ_05" --backend matplotlib

  # Generate a CSV inventory of all timelapse series across data/raw
  focipy catalog data/raw -o data/processed/raw_series_catalog.csv

Run 'focipy help <command>' or 'focipy <command> --help' for command-specific options.\
"""


def _build_parser() -> tuple[
    argparse.ArgumentParser, dict[str, argparse.ArgumentParser]
]:
    fmt = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(
        prog="focipy",
        description=(
            "FociPy — Automated kinetics analysis of DNA repair protein "
            "recruitment at laser-induced damage sites."
        ),
        formatter_class=fmt,
        add_help=False,
    )
    parser.add_argument(
        "-h", "--help", action="store_true", help="Show this help message and exit"
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"focipy {__version__}",
        help="Show program version and exit",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # focipy help [command]
    help_parser = subparsers.add_parser(
        "help",
        help="Show general manual or detailed help for a command",
        description="Display usage manual or detailed options for a subcommand.",
        formatter_class=fmt,
    )
    help_parser.add_argument(
        "topic",
        nargs="?",
        choices=["info", "view", "catalog"],
        default=None,
        metavar="command",
        help="Command name to inspect (info, view, catalog)",
    )

    # focipy info <file.lif>
    info_parser = subparsers.add_parser(
        "info",
        help="Inspect series metadata, dimensions, and laser ROIs in a .lif file",
        description=(
            "Parse the XML header of a Leica .lif file and print a summary table\n"
            "of image series, dimensions (T, C, Y, X), duration, pixel size,\n"
            "pre-bleach frame count, and laser microirradiation target coordinates.\n"
            "Multi-phase FRAP acquisitions (FRAP Series + Pb2/Pb3) are merged."
        ),
        epilog=(
            "EXAMPLES\n"
            '  focipy info "data/raw/XRCC1/2026_02_26/'
            '2026_02_26 HeLa mRFP-XRCC1 12uJ.lif"\n'
            '  focipy info "data/raw/53BP1/2026_05_06/'
            '20260506_mCH-53BP1 HeLa.lif" --timelapse-only\n'
            '  focipy info "data/raw/XRCC1/2026_02_26/'
            '2026_02_26 HeLa mRFP-XRCC1 25uJ.lif" --no-merge'
        ),
        formatter_class=fmt,
    )
    info_parser.add_argument(
        "path", type=Path, metavar="file.lif", help="Path to input Leica .lif file"
    )
    info_parser.add_argument(
        "--timelapse-only",
        action="store_true",
        help="List only multi-frame timelapse series (T > 1)",
    )
    info_parser.add_argument(
        "--include-snapshots",
        action="store_true",
        help="Include screenshot (Snapshot) series in the output table",
    )
    info_parser.add_argument(
        "--no-merge",
        action="store_true",
        help="Do not merge multi-phase FRAP Series and FRAP Pb2/Pb3 series",
    )

    # focipy view <file.lif>
    view_parser = subparsers.add_parser(
        "view",
        help="Launch interactive timelapse viewer (Napari or Matplotlib)",
        description=(
            "Load a timelapse series from a Leica .lif file and open an interactive\n"
            "viewer with overlaid laser target crosshairs (+) and circular ROI\n"
            "measurement regions. Uses Napari when installed, falling back to an\n"
            "interactive Matplotlib time-slider window."
        ),
        epilog=(
            "EXAMPLES\n"
            '  focipy view "data/raw/XRCC1/2026_02_26/'
            '2026_02_26 HeLa mRFP-XRCC1 12uJ.lif" -s 3\n'
            '  focipy view "data/raw/XRCC1/2026_02_26/'
            '2026_02_26 HeLa mRFP-XRCC1 12uJ.lif" -s "12uJ_05"\n'
            '  focipy view "data/raw/53BP1/2026_05_06/'
            '20260506_mCH-53BP1 HeLa.lif" -s 2 --backend matplotlib'
        ),
        formatter_class=fmt,
    )
    view_parser.add_argument(
        "path", type=Path, metavar="file.lif", help="Path to input Leica .lif file"
    )
    view_parser.add_argument(
        "-s",
        "--series",
        default=None,
        metavar="SERIES",
        help="Series index (e.g. 4) or name substring (e.g. '25uJ_01')",
    )
    view_parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=None,
        metavar="FILE",
        help="Path to YAML configuration file (reads kinetics.roi_radius_px)",
    )
    view_parser.add_argument(
        "--backend",
        choices=["auto", "napari", "matplotlib"],
        default="auto",
        help="Visualization backend: auto, napari, or matplotlib (default: auto)",
    )
    view_parser.add_argument(
        "--no-merge",
        action="store_true",
        help="Do not merge multi-phase FRAP Series and FRAP Pb2/Pb3 series",
    )

    # focipy catalog [dir]
    cat_parser = subparsers.add_parser(
        "catalog",
        help="Scan a directory of .lif files and export a metadata table (.csv)",
        description=(
            "Recursively scan a directory of Leica .lif files, extract acquisition,\n"
            "optical, laser, detector, and ROI metadata from XML headers, and save\n"
            "a unified inventory table in CSV format."
        ),
        epilog=(
            "EXAMPLES\n"
            "  focipy catalog\n"
            "  focipy catalog data/raw -o data/processed/raw_series_catalog.csv\n"
            "  focipy catalog data/raw --include-static "
            "-o data/processed/all_series.csv"
        ),
        formatter_class=fmt,
    )
    cat_parser.add_argument(
        "root_dir",
        type=Path,
        nargs="?",
        default=Path("data/raw"),
        metavar="dir",
        help="Root directory (or single .lif file) to scan (default: data/raw)",
    )
    cat_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("data/processed/raw_series_catalog.csv"),
        metavar="FILE",
        help="Output CSV file path (default: data/processed/raw_series_catalog.csv)",
    )
    cat_parser.add_argument(
        "--include-static",
        action="store_true",
        help="Include single-frame static preview images (T = 1) in the catalog",
    )
    cat_parser.add_argument(
        "--no-merge",
        action="store_true",
        help="Keep FRAP Series and FRAP Pb2/Pb3 series as separate rows",
    )

    submap = {
        "info": info_parser,
        "view": view_parser,
        "catalog": cat_parser,
    }
    return parser, submap


def main() -> None:
    parser, subparser_map = _build_parser()
    args = parser.parse_args()

    if args.help or args.command is None:
        print(HELP_OVERVIEW)
        return

    if args.command == "help":
        if args.topic in subparser_map:
            subparser_map[args.topic].print_help()
        else:
            print(HELP_OVERVIEW)
    elif args.command == "info":
        list_lif_series(
            args.path,
            exclude_snapshots=not args.include_snapshots,
            only_timelapse=args.timelapse_only,
            merge_pb_series=not args.no_merge,
        )
    elif args.command == "view":
        cfg = (
            PipelineConfig.from_yaml(args.config)
            if args.config
            else PipelineConfig.from_yaml()
        )
        series_arg: int | str | None = args.series
        if isinstance(series_arg, str) and series_arg.isdigit():
            series_arg = int(series_arg)
        view_lif_series(
            args.path,
            series=series_arg,
            roi_radius_px=cfg.kinetics.roi_radius_px,
            backend=args.backend,
            merge_pb_series=not args.no_merge,
        )
    elif args.command == "catalog":
        df = catalog_lif_files(
            args.root_dir,
            output_csv=args.output,
            only_timelapse=not args.include_static,
            merge_pb_series=not args.no_merge,
        )
        n_files = df["file_name"].nunique() if not df.empty else 0
        print(
            f"Catalog exported: {len(df)} series across {n_files} .lif files "
            f"-> {args.output}"
        )


if __name__ == "__main__":
    main()
