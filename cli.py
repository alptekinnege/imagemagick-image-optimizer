import argparse
import sys
from pathlib import Path
from typing import Optional

from core import (
    DEFAULT_EXTENSIONS,
    parse_extensions,
    process_images,
)

VERSION = "0.2.0"


def _validate_positive(value: Optional[str], name: str):
    if value is None:
        return None
    try:
        v = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{name} must be an integer.")
    if v <= 0:
        raise argparse.ArgumentTypeError(f"{name} must be a positive integer.")
    return v


def _validate_quality(value: Optional[str]):
    if value is None:
        return None
    try:
        v = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("--quality must be an integer between 1 and 100.")
    if v < 1 or v > 100:
        raise argparse.ArgumentTypeError("--quality must be between 1 and 100.")
    return v


def _validate_suffix(value: str) -> str:
    if not value.strip():
        raise argparse.ArgumentTypeError("--suffix cannot be empty.")
    p = Path(value)
    if p.name != value:
        raise argparse.ArgumentTypeError("--suffix must not contain path separators.")
    return value


def _validate_output_format(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    fmt = value.lower().lstrip(".")
    if not fmt:
        raise argparse.ArgumentTypeError("--format cannot be empty.")
    if "/" in fmt or "\\" in fmt or Path(fmt).name != fmt:
        raise argparse.ArgumentTypeError("--format must not contain path separators.")
    return fmt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resize and optimize images with ImageMagick."
    )
    parser.add_argument("--input", "-i", required=True, help="Input folder")
    parser.add_argument(
        "--suffix",
        required=True,
        type=_validate_suffix,
        help="Suffix added before extension, e.g. _resized",
    )
    parser.add_argument(
        "--max-width",
        type=lambda v: _validate_positive(v, "--max-width"),
        help="Maximum width in pixels",
    )
    parser.add_argument(
        "--max-height",
        type=lambda v: _validate_positive(v, "--max-height"),
        help="Maximum height in pixels",
    )
    parser.add_argument("--recursive", action="store_true", help="Process subfolders")
    parser.add_argument(
        "--extensions",
        type=parse_extensions,
        help="Comma-separated list of extensions (default: common image types)",
    )
    parser.add_argument("--magick-path", help="Path to magick executable (optional)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite outputs")
    parser.add_argument("--dry-run", action="store_true", help="Print commands only")
    parser.add_argument(
        "--quality",
        type=_validate_quality,
        help="JPEG/WebP compression quality (1-100)",
    )
    parser.add_argument(
        "--strip", action="store_true", help="Strip metadata (EXIF, profiles)"
    )
    parser.add_argument(
        "--sharpen",
        help="Sharpen after resize (ImageMagick sharpen arg, e.g. '0x1')",
    )
    parser.add_argument(
        "--output-dir",
        help="Write output files to a separate directory (preserves subfolder structure)",
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        type=_validate_output_format,
        help="Convert images to this format (e.g. webp, jpg, png)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.max_width is None and args.max_height is None:
        parser.error("At least one of --max-width or --max-height is required.")

    input_dir = Path(args.input)
    if not input_dir.exists() or not input_dir.is_dir():
        parser.error("--input must be a directory.")

    output_dir = Path(args.output_dir) if args.output_dir else None

    stats = process_images(
        input_dir=input_dir,
        suffix=args.suffix,
        max_width=args.max_width,
        max_height=args.max_height,
        recursive=args.recursive,
        extensions=args.extensions,
        magick_path=args.magick_path,
        quality=args.quality,
        strip=args.strip,
        sharpen=args.sharpen,
        output_dir=output_dir,
        output_format=args.output_format,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )

    print("Done")
    print(f"Geometry: {stats['geometry']}")
    print(f"Scanned: {stats['total']}")
    if args.dry_run:
        print(f"Would process: {stats['would_process']}")
    else:
        print(f"Processed: {stats['processed']}")
    print(f"Skipped (suffix): {stats['skipped_suffix']}")
    print(f"Skipped (existing): {stats['skipped_existing']}")
    print(f"Skipped (extension): {stats['skipped_extension']}")
    print(f"Errors: {stats['errors']}")
    print(f"Elapsed: {stats['elapsed']:.2f}s")


if __name__ == "__main__":
    main()
