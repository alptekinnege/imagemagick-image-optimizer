import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import perf_counter
from typing import Optional, Set

DEFAULT_EXTENSIONS: Set[str] = {
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


def parse_extensions(value: str) -> Set[str]:
    items = [v.strip().lower().lstrip(".") for v in value.split(",") if v.strip()]
    if not items:
        raise ValueError("Extensions list is empty.")
    return set(items)


def build_geometry(
    max_width: Optional[int], max_height: Optional[int]
) -> str:
    if max_width and max_height:
        return f"{max_width}x{max_height}"
    if max_width:
        return f"{max_width}x"
    return f"x{max_height}"


def resolve_magick(path_override: Optional[str]) -> str:
    if path_override:
        path = Path(path_override)
        if not path.exists():
            print(f"magick not found at: {path}", file=sys.stderr)
            sys.exit(2)
        return str(path)

    magick = shutil.which("magick")
    if magick:
        return magick

    print(
        "magick not found in PATH. Install ImageMagick and ensure 'magick' is available.",
        file=sys.stderr,
    )
    sys.exit(2)


def iter_files(input_dir: Path, recursive: bool):
    return input_dir.rglob("*") if recursive else input_dir.iterdir()


def process_images(
    input_dir: Path,
    suffix: str,
    *,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    recursive: bool = False,
    extensions: Optional[Set[str]] = None,
    magick_path: Optional[str] = None,
    quality: Optional[int] = None,
    strip: bool = False,
    sharpen: Optional[str] = None,
    output_dir: Optional[Path] = None,
    output_format: Optional[str] = None,
    overwrite: bool = False,
    dry_run: bool = False,
) -> dict:
    magick = resolve_magick(magick_path)
    geometry = build_geometry(max_width, max_height)
    extensions = extensions or DEFAULT_EXTENSIONS

    command = [magick]
    extra_args: list[str] = ["-resize", geometry]
    if quality is not None:
        extra_args.extend(["-quality", str(quality)])
    if strip:
        extra_args.append("-strip")
    if sharpen:
        extra_args.extend(["-sharpen", sharpen])

    stats = {
        "total": 0,
        "processed": 0,
        "would_process": 0,
        "skipped_suffix": 0,
        "skipped_existing": 0,
        "skipped_extension": 0,
        "errors": 0,
    }

    start = perf_counter()
    created_dirs: Set[Path] = set()

    tasks = []

    for path in iter_files(input_dir, recursive):
        if not path.is_file():
            continue

        stats["total"] += 1
        ext = path.suffix.lower().lstrip(".")
        if ext not in extensions:
            stats["skipped_extension"] += 1
            continue

        if path.stem.endswith(suffix):
            stats["skipped_suffix"] += 1
            continue

        out_ext = f".{output_format}" if output_format else path.suffix
        output_filename = f"{path.stem}{suffix}{out_ext}"

        if output_dir:
            rel = path.relative_to(input_dir)
            out_path = output_dir / rel.parent / output_filename
        else:
            out_path = path.with_name(output_filename)

        if out_path.exists() and not overwrite:
            stats["skipped_existing"] += 1
            continue

        cmd = command + [str(path)] + extra_args + [str(out_path)]
        if dry_run:
            stats["would_process"] += 1
            print("DRY-RUN:", " ".join(cmd))
            continue

        parent = out_path.parent
        if parent not in created_dirs:
            parent.mkdir(parents=True, exist_ok=True)
            created_dirs.add(parent)
        tasks.append((path, cmd))

    def run_command(task):
        path, cmd = task
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return path, result

    if tasks:
        with ThreadPoolExecutor() as executor:
            for path, result in executor.map(run_command, tasks):
                if result.returncode != 0:
                    stats["errors"] += 1
                    print(f"ERROR: {path}", file=sys.stderr)
                    if result.stderr:
                        print(result.stderr.strip(), file=sys.stderr)
                else:
                    stats["processed"] += 1

    elapsed = perf_counter() - start
    stats["elapsed"] = elapsed
    stats["geometry"] = geometry

    return stats
