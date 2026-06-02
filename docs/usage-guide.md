# Usage Guide

## Table of Contents

- [How Resizing Works](#how-resizing-works)
- [Output Naming](#output-naming)
- [All Options](#all-options)
- [Workflows](#workflows)
- [Output Summary](#output-summary)
- [Error Handling](#error-handling)
- [Architecture & API](#architecture--api)
- [FAQ](#faq)

---

## How Resizing Works

The tool tells ImageMagick to resize each image to **fit within** a bounding box. It never stretches or crops. The aspect ratio is always preserved.

| You specify | Geometry | Behavior |
|-------------|----------|----------|
| `--max-width 800 --max-height 600` | `800x600` | Scale down to fit in an 800×600 box. Whichever dimension hits first wins. |
| `--max-width 800` | `800x` | Scale to 800 px wide, height follows proportionally. |
| `--max-height 600` | `x600` | Scale to 600 px tall, width follows proportionally. |

**Example:** A 2000×1200 photo with `--max-width 800 --max-height 600` becomes 800×480. Width hits first (2000→800 = 2.5× reduction). Height: 1200/2.5 = 480, which fits under 600.

**Upscaling note:** Images *smaller* than the target dimensions are left untouched. If you need upscaling, that requires a different ImageMagick flag — this tool focuses on downscaling for optimization.

---

## Output Naming

### Basic suffix

The output filename is built by inserting the suffix before the extension:

```
Input:    photo.jpg
Suffix:   _resized
Output:   photo_resized.jpg
```

```
Input:    vacation/sunset.png
Suffix:   _800w
Output:   vacation/sunset_800w.png
```

### With format conversion

When `--format` is used, the extension changes but the stem logic stays the same:

```
Input:    photo.png
Suffix:   _opt
Format:   webp
Output:   photo_opt.webp
```

### With output directory

When `--output-dir` is used, the folder structure relative to the input directory is preserved:

```
photos/             →  optimized/
  hero.jpg                           hero_opt.jpg
  blog/                               blog/
    post1.png                          post1_opt.webp
    post2.png                          post2_opt.webp
```

Without `--recursive`, only the top-level files are processed. Subdirectories are ignored.

### Skip logic

A file is skipped when any of these conditions is true:

1. **Filename already ends with the suffix** — prevents reprocessing output files from a previous run. Example: `photo_resized.jpg` is skipped when `--suffix _resized`.
2. **Output file already exists** and `--overwrite` is not set — protects existing work. Use `--overwrite` to force reprocessing.
3. **Extension is not in the allowed list** — skips non-image files like `.txt`, `.html`, `.zip`, or image formats you didn't include with `--extensions`.

---

## All Options

### `--input`, `-i`

**Required.** Path to the folder containing images. Must exist and be a directory.

```bash
--input "C:\Users\me\Pictures"
--input "./assets"
--input /var/www/images
```

### `--suffix`

**Required.** String appended to each filename before the extension. Use an empty string `""` when you just want to convert formats without renaming (combine with `--overwrite` or `--output-dir`).

```bash
--suffix "_opt"      # photo.jpg → photo_opt.jpg
--suffix "_800w"     # hero.png  → hero_800w.png
--suffix ""          # image.png → image.png  (useful with --format)
```

Validation: suffix cannot be empty when used alone, cannot contain path separators (`/` or `\`).

### `--max-width`

Maximum width in pixels. Images wider than this are scaled down; narrower ones stay as-is.

```bash
--max-width 1920     # Full HD width
--max-width 800      # Typical blog content width
--max-width 300      # Thumbnail
```

### `--max-height`

Maximum height in pixels. Same behavior as `--max-width` but controls height.

```bash
--max-height 1080    # Full HD height
--max-height 600     # Common vertical limit
```

At least one of `--max-width` or `--max-height` is required. Both must be positive integers.

### `--recursive`

Walk through all subdirectories instead of only the top-level folder.

```bash
--recursive
```

Without this flag, only files directly inside `--input` are processed — subdirectories and their contents are ignored.

### `--extensions`

Comma-separated list of file extensions to process. Case-insensitive, dots optional.

```bash
--extensions "jpg,png,webp"
--extensions ".JPG,.PNG,.GIF"
--extensions "jpeg,jpg"                # JPEG only
```

**Default:** `jpg, jpeg, png, webp, avif, tif, tiff, bmp, gif`

Use this to restrict processing to specific image types, skipping HEIC, RAW, SVG, or other formats you don't want touched.

### `--quality`

Sets JPEG/WebP compression quality. Range: 1–100. Lower = smaller files, worse quality.

```bash
--quality 85    # Good balance for web (default in many tools)
--quality 60    # Aggressive compression, visible artifacts
--quality 95    # Near-lossless
```

**Per-format behavior:**
- **JPEG:** Direct quality control. 85 is the sweet spot for web.
- **WebP:** Maps to WebP quality. Similar scale to JPEG.
- **PNG:** This flag has **no effect** — PNG is lossless. ImageMagick ignores it silently.
- **AVIF:** Supported in ImageMagick 7.1+.

### `--strip`

Removes all metadata from the output: EXIF data, ICC color profiles, thumbnails, comments, GPS coordinates, XMP data, IPTC data. Reduces file size, sometimes significantly (100KB+ on photos from modern cameras).

```bash
--strip
```

**When to use:** Almost always for web images — nobody needs your camera make/model, GPS coordinates, or embedded thumbnail in a web asset.

**When to skip:** If you need to preserve copyright info, camera settings for later editing, or color profiles for print workflows.

**Size impact examples:**
- iPhone photo with GPS + EXIF: 50-200KB of metadata
- Screenshot: typically <1KB (minimal metadata)
- Stock photo with full IPTC/XMP: 10-50KB

### `--sharpen`

Applies ImageMagick's `-sharpen` operator after resizing. Downscaling naturally softens images; sharpening compensates for this.

```bash
--sharpen "0x1"     # Mild sharpening (good default)
--sharpen "0x1.5"   # Stronger — visible halos possible
--sharpen "0x0.5"   # Subtle — barely noticeable
--sharpen "0x0.3"   # Very subtle for already-sharp images
```

The format is `radius x sigma`. When radius is `0`, ImageMagick auto-calculates it. Sigma controls the strength — larger values = stronger effect.

**Recommendation:** Use `0x1` for most downscaled photos. Skip for screenshots or already-sharp computer graphics.

### `--output-dir`

Write output files to a separate directory instead of alongside the originals. The directory is created if it doesn't exist. Subfolder structure is preserved when used with `--recursive`.

```bash
--output-dir "optimized"
--output-dir "./web-ready"
--output-dir "/var/www/static/img"
```

This is the safest mode — your originals are never in the same folder as the output. Combine with `--suffix ""` and `--recursive` to mirror an entire directory structure.

### `--format`

Convert all output images to a single format. The extension changes but the filename stem logic stays the same.

```bash
--format webp    # Everything becomes .webp
--format jpg     # Everything becomes .jpg
--format png     # Everything becomes .png
--format avif    # Everything becomes .avif (IM 7.1+)
```

ImageMagick handles the conversion automatically. PNGs converted to JPEG will have a white background (no transparency support). WebP supports both lossy and lossless modes depending on `--quality`.

### `--overwrite`

Overwrite output files if they already exist. Without this flag, existing outputs are skipped (counted as "Skipped (existing)").

```bash
--overwrite
```

Useful when re-running a batch with different quality settings or after source images have changed.

### `--dry-run`

Print every ImageMagick command that *would* run, without actually executing anything.

```bash
--dry-run
```

Sample output:
```
DRY-RUN: magick photos/img001.jpg -resize 1920x -quality 85 -strip photos/img001_opt.jpg
DRY-RUN: magick photos/img002.jpg -resize 1920x -quality 85 -strip photos/img002_opt.jpg
```

Use this to sanity-check your arguments before processing thousands of files. Review the commands, then remove `--dry-run` and run for real.

### `--magick-path`

Full path to the `magick` executable if it's not in your PATH.

```bash
--magick-path "C:\Program Files\ImageMagick\magick.exe"
```

### `--version`

Print the tool version and exit.

```bash
--version
# Output: optimizer.py 0.2.0
```

---

## Workflows

### Web-ready photo gallery (most common)

Resize to a max dimension, compress JPEG, strip metadata, sharpen slightly, output to separate folder:

```bash
python optimizer.py -i "raw_photos" --suffix "_web" \
  --max-width 1920 --max-height 1920 \
  --quality 82 --strip --sharpen "0x1" \
  --output-dir "web_gallery"
```

This converts a folder of high-res camera photos into web-optimized JPEGs ready for a gallery page.

### Convert PNGs to WebP in-place

```bash
python optimizer.py -i "assets" --suffix "" --format webp --overwrite
```

Removes original PNGs and replaces them with WebP versions. **Be careful** — this modifies the source folder. Better to use `--output-dir` for safety.

### Preview before bulk processing

```bash
python optimizer.py -i "10k_photos" --suffix "_opt" --max-width 1920 --recursive --dry-run
```

Review the printed commands, estimate runtime from the file count, then remove `--dry-run` and run for real.

### Thumbnail generation

```bash
python optimizer.py -i "photos" --suffix "_thumb" \
  --max-width 300 --max-height 300 \
  --quality 70 --strip --sharpen "0x0.5" \
  --output-dir "thumbs"
```

Creates square-ish thumbnails (max 300×300), mild sharpening since the images are tiny.

### Process only JPEGs, ignore everything else

```bash
python optimizer.py -i "mixed_folder" --suffix "_opt" \
  --max-width 1920 --extensions "jpg,jpeg"
```

RAW files, PNGs, GIFs are all skipped. Only JPEGs are touched.

### Maximum compression (smallest possible files)

```bash
python optimizer.py -i "photos" --suffix "_tiny" \
  --max-width 800 --quality 40 --strip --format webp
```

Produces extremely small WebP files (low quality) at 800px wide. Good for bandwidth-constrained use cases.

### Mirror a directory structure with optimization

```bash
python optimizer.py -i "site/images" --suffix "" \
  --max-width 1920 --recursive \
  --quality 85 --strip --format webp \
  --output-dir "site/images_webp"
```

Replicates the entire `site/images` tree under `site/images_webp` with all images resized and converted to WebP.

---

## Output Summary

After processing, the tool prints a summary:

```
Done
Geometry: 1920x
Scanned: 147
Processed: 142
Skipped (suffix): 0
Skipped (existing): 3
Skipped (extension): 2
Errors: 0
Elapsed: 12.34s
```

| Field | Meaning |
|-------|---------|
| **Geometry** | The ImageMagick geometry string that was used |
| **Scanned** | Total files examined in the input directory (including non-images) |
| **Processed** | Images that were successfully resized/optimized |
| **Would process** | (dry-run only) Images that would be processed |
| **Skipped (suffix)** | Files whose names already end with the suffix — likely outputs from a prior run |
| **Skipped (existing)** | Output files already exist and `--overwrite` was not used |
| **Skipped (extension)** | Files with extensions not in the allowed list (`.txt`, `.html`, etc.) |
| **Errors** | Files where ImageMagick returned a non-zero exit code |
| **Elapsed** | Wall-clock time from start to finish |

---

## Error Handling

The tool uses a **per-file** error model. If one image fails (corrupt file, unsupported format, disk full), processing continues with the next image. The error is printed to stderr along with ImageMagick's error message, and the count is reflected in the summary's `Errors` field.

Example error output:
```
ERROR: photos/corrupt.jpg
magick: Corrupt JPEG data: 42 extraneous bytes before marker 0xd9 `photos/corrupt.jpg'
```

Only two errors cause an immediate exit (exit code 2):
- `magick` executable not found (check `--magick-path` or install ImageMagick)
- `--input` directory does not exist or is not a directory

Argument validation errors (negative values, empty suffix, missing required args) exit with code 2 after argparse prints the error.

---

## Architecture & API

The codebase is split into three modules:

```
optimizer.py  →  Entry point, delegates to cli.main()
cli.py        →  Argparse-based CLI, argument validation, output summary
core.py       →  Pure logic: file iteration, command building, subprocess calls
```

- **`core.py`** has no argparse dependency — it takes plain arguments and returns a stats dict. This makes it testable without monkeypatching `sys.argv`.
- **`cli.py`** handles all user-facing concerns: parsing, validation, error messages, and the human-readable summary.
- **`optimizer.py`** is the backwards-compatible entry point for `python optimizer.py`.

### `core.process_images()` API

```python
from pathlib import Path
from core import process_images

stats = process_images(
    input_dir=Path("photos"),
    suffix="_opt",
    max_width=1920,
    max_height=1080,
    recursive=True,
    extensions={"jpg", "png", "webp"},
    quality=85,
    strip=True,
    sharpen="0x1",
    output_dir=Path("optimized"),
    output_format="webp",
    overwrite=False,
    dry_run=True,
)

print(stats["total"])          # int
print(stats["processed"])      # int
print(stats["errors"])         # int
print(stats["elapsed"])        # float (seconds)
print(stats["geometry"])       # str
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_dir` | `Path` | Yes | — | Directory containing images |
| `suffix` | `str` | Yes | — | String to append before extension |
| `max_width` | `int \| None` | — | `None` | Maximum width in pixels |
| `max_height` | `int \| None` | — | `None` | Maximum height in pixels |
| `recursive` | `bool` | — | `False` | Process subdirectories |
| `extensions` | `Set[str] \| None` | — | `DEFAULT_EXTENSIONS` | Allowed file extensions |
| `magick_path` | `str \| None` | — | `None` | Path to magick binary |
| `quality` | `int \| None` | — | `None` | JPEG/WebP quality 1-100 |
| `strip` | `bool` | — | `False` | Remove metadata |
| `sharpen` | `str \| None` | — | `None` | Sharpen argument (e.g. `"0x1"`) |
| `output_dir` | `Path \| None` | — | `None` | Separate output directory |
| `output_format` | `str \| None` | — | `None` | Convert to format (e.g. `"webp"`) |
| `overwrite` | `bool` | — | `False` | Overwrite existing files |
| `dry_run` | `bool` | — | `False` | Print commands only |

All parameters after `suffix` are keyword-only.

#### Return Value

Returns a `dict` with these keys:

| Key | Type | Description |
|-----|------|-------------|
| `total` | `int` | All files scanned |
| `processed` | `int` | Successfully resized (0 in dry-run) |
| `would_process` | `int` | Would be processed in dry-run |
| `skipped_suffix` | `int` | Skipped due to filename suffix match |
| `skipped_existing` | `int` | Skipped because output exists |
| `skipped_extension` | `int` | Skipped due to unsupported extension |
| `errors` | `int` | ImageMagick failures |
| `elapsed` | `float` | Wall-clock time in seconds |
| `geometry` | `str` | ImageMagick geometry string used |

### Key Functions

```python
core.parse_extensions(value: str) -> Set[str]
```
Parses a comma-separated extension string. Strips dots, lowercases, returns a set. Raises `ValueError` if empty.

```python
core.build_geometry(max_width: Optional[int], max_height: Optional[int]) -> str
```
Builds the ImageMagick geometry string from width/height. Returns `"WxH"`, `"Wx"`, or `"xH"`.

```python
core.resolve_magick(path_override: Optional[str]) -> str
```
Finds the `magick` binary. Checks the override path first, then PATH. Calls `sys.exit(2)` if not found.

---

## FAQ

### Does it overwrite my originals?

No. Output files have a suffix (or different extension via `--format`), so they never match original filenames. If you use `--output-dir`, output goes to an entirely different folder. The only way to accidentally overwrite is `--overwrite` combined with `--suffix ""` and `--format` matching the original extension. If you're worried, always use `--dry-run` first.

### Why are some of my images skipped?

Check the summary output. Each skip reason is counted separately:

- **"Skipped (suffix)"** — the filename already ends with your suffix string. This prevents reprocessing output files from a previous run. Use a different suffix.
- **"Skipped (existing)"** — the output file already exists. Use `--overwrite` to force reprocessing.
- **"Skipped (extension)"** — the file type isn't in the allowed list. Add it with `--extensions`.

### Does it support animated GIFs?

It processes GIF files as images but does **not** preserve animation. Each GIF is treated as a single frame (the first frame is used). If you need animated GIF optimization, use a dedicated tool like `gifsicle`.

### Can I run it on a folder with thousands of images?

Yes. Each image is processed independently through a subprocess, so a corrupt file won't crash the batch. Memory usage is low since ImageMagick handles the images in its own process. For extremely large batches, use `--dry-run` first to validate the commands and estimate the scope.

No progress bar is shown during processing — you'll see error output for failures only, then the final summary.

### What's the difference between `--quality` and `--strip`?

**`--quality`** controls lossy compression level for JPEG and WebP. Lower = more compression, lower visual quality, smaller file. This affects the actual pixel data.

**`--strip`** removes hidden metadata like EXIF data, GPS coordinates, camera make/model, color profiles, and embedded thumbnails. These can add significant bytes (up to 200KB on modern phone photos) **without affecting visual quality at all**.

Use both together for maximum size reduction with minimal visible quality loss.

### Does it work on macOS and Linux?

Yes. The tool uses `shutil.which("magick")` to find ImageMagick, which works cross-platform. Path separators are handled by `pathlib.Path`. The CI runs on Ubuntu.

### What ImageMagick version do I need?

ImageMagick 7+ (the `magick` command). Version 6 uses separate `convert`, `mogrify`, etc. commands and is not supported. Check with `magick --version`.

### Can I use it as a library in my own Python code?

Yes. Import `core.process_images()` directly:

```python
from pathlib import Path
from core import process_images

stats = process_images(
    input_dir=Path("images"),
    suffix="_opt",
    max_width=1200,
    quality=85,
    strip=True,
)
```

The function has no dependency on argparse or CLI machinery.
