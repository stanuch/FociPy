"""Helper script to sort incoming .lif/.maf files in data/raw/ by protein & date."""

import re
import shutil
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DATE_PATTERN = re.compile(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})")


def classify_group(filename: str) -> str:
    upper = filename.upper()
    if "PSF" in upper or "LAMBDA" in upper:
        return "calibration"
    if "53BP1" in upper:
        return "53BP1"
    if "XRCC1" in upper:
        return "XRCC1"
    return "other"


def extract_date_folder(filename: str) -> str | None:
    match = DATE_PATTERN.search(filename)
    if match:
        y, m, d = match.groups()
        return f"{y}_{m}_{d}"
    return None


def sort_raw_files(raw_dir: Path = RAW_DIR) -> None:
    if not raw_dir.is_dir():
        print(f"Directory not found: {raw_dir}")
        return

    for file_path in sorted(raw_dir.iterdir()):
        if not file_path.is_file() or file_path.suffix.lower() not in {".lif", ".maf"}:
            continue

        group = classify_group(file_path.name)
        date_folder = extract_date_folder(file_path.name)

        if group == "calibration" or date_folder is None:
            dest_dir = raw_dir / group
        else:
            dest_dir = raw_dir / group / date_folder

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / file_path.name
        shutil.move(str(file_path), str(dest_path))
        print(f"Moved: {file_path.name} -> {dest_path.relative_to(raw_dir)}/")


if __name__ == "__main__":
    sort_raw_files()
