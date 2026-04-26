import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from time import perf_counter

DEFAULT_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "avif",
    "tif",
    "tiff",
    "bmp",
    "gif",
}


def parse_extensions(value):
    items = [v.strip().lower().lstrip(".") for v in value.split(",") if v.strip()]
    if not items:
        raise argparse.ArgumentTypeError("Extensions list is empty.")
    return set(items)


def build_geometry(max_width, max_height):
    if max_width and max_height:
        return f"{max_width}x{max_height}"
    if max_width:
        return f"{max_width}x"
    return f"x{max_height}"


def resolve_magick(path_override):
    if path_override:
        path = Path(path_override)
        if not path.exists():
            print(f"magick not found at: {path}", file=sys.stderr)
            sys.exit(2)
        return str(path)

    magick = shutil.which("magick")
    if magick:
        return magick

    convert = shutil.which("convert")
    if convert:
        return convert

    print(
        "ImageMagick command not found in PATH. Install ImageMagick and ensure "
        "'magick' or 'convert' is available.",
        file=sys.stderr,
    )
    sys.exit(2)


def iter_files(input_dir, recursive):
    return input_dir.rglob("*") if recursive else input_dir.iterdir()


def main():
    parser = argparse.ArgumentParser(
        description="Resize images with ImageMagick while keeping original format."
    )
    parser.add_argument("--input", "-i", required=True, help="Input folder")
    parser.add_argument(
        "--suffix",
        required=True,
        help="Suffix added before extension, for example: _resized",
    )
    parser.add_argument("--max-width", type=int, help="Maximum width in pixels")
    parser.add_argument("--max-height", type=int, help="Maximum height in pixels")
    parser.add_argument("--recursive", action="store_true", help="Process subfolders")
    parser.add_argument(
        "--extensions",
        type=parse_extensions,
        help="Comma-separated list of extensions (default: common image types)",
    )
    parser.add_argument("--magick-path", help="Path to magick.exe (optional)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite outputs")
    parser.add_argument("--dry-run", action="store_true", help="Print commands only")

    args = parser.parse_args()

    if args.max_width is None and args.max_height is None:
        parser.error("At least one of --max-width or --max-height is required.")
    if args.max_width is not None and args.max_width <= 0:
        parser.error("--max-width must be a positive integer.")
    if args.max_height is not None and args.max_height <= 0:
        parser.error("--max-height must be a positive integer.")

    suffix = args.suffix
    if not suffix.strip():
        parser.error("--suffix cannot be empty.")
    if Path(suffix).name != suffix:
        parser.error("--suffix must not contain path separators.")

    input_dir = Path(args.input)
    if not input_dir.exists() or not input_dir.is_dir():
        parser.error("--input must be a directory.")

    magick = resolve_magick(args.magick_path)
    geometry = build_geometry(args.max_width, args.max_height)
    extensions = args.extensions or DEFAULT_EXTENSIONS

    total = 0
    processed = 0
    would_process = 0
    skipped_suffix = 0
    skipped_existing = 0
    skipped_extension = 0
    errors = 0

    start = perf_counter()

    for path in iter_files(input_dir, args.recursive):
        if not path.is_file():
            continue

        total += 1
        ext = path.suffix.lower().lstrip(".")
        if ext not in extensions:
            skipped_extension += 1
            continue

        if path.stem.endswith(suffix):
            skipped_suffix += 1
            continue

        output_path = path.with_name(f"{path.stem}{suffix}{path.suffix}")
        if output_path.exists() and not args.overwrite:
            skipped_existing += 1
            continue

        command = [magick, str(path), "-resize", geometry, str(output_path)]
        if args.dry_run:
            would_process += 1
            print("DRY-RUN:", " ".join(command))
            continue

        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode != 0:
            errors += 1
            print(f"ERROR: {path}", file=sys.stderr)
            if result.stderr:
                print(result.stderr.strip(), file=sys.stderr)
            continue

        processed += 1

    elapsed = perf_counter() - start

    print("Done")
    print(f"Geometry: {geometry}")
    print(f"Scanned: {total}")
    if args.dry_run:
        print(f"Would process: {would_process}")
    else:
        print(f"Processed: {processed}")
    print(f"Skipped (suffix): {skipped_suffix}")
    print(f"Skipped (existing): {skipped_existing}")
    print(f"Skipped (extension): {skipped_extension}")
    print(f"Errors: {errors}")
    print(f"Elapsed: {elapsed:.2f}s")


if __name__ == "__main__":
    main()
