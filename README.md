# ImageMagick Image Optimizer

Batch resize and optimize images with ImageMagick. Resize proportionally, compress, strip metadata, sharpen, convert formats, and output to a separate directory — all in one pass.

## Installation

**Requirements:** Python 3.8+, ImageMagick 7+ with `magick` in PATH.

```bash
pip install imagemagick-image-optimizer
```

Or for local dev:

```bash
git clone <repo>
cd imagemagick-image-optimizer
pip install -e .
```

After install, `img-optimize` is available globally. You can also run `python optimizer.py`.

## Quick Start

```bash
# Resize to 800px wide
python optimizer.py -i "photos" --suffix "_small" --max-width 800

# Compress and strip metadata too
python optimizer.py -i "photos" --suffix "_small" --max-width 800 --quality 80 --strip

# Convert to WebP, separate output folder
python optimizer.py -i "photos" --suffix "" --max-width 1920 --format webp --output-dir "optimized"

# Preview commands without running
python optimizer.py -i "photos" --suffix "_opt" --max-width 1920 --dry-run
```

## How Resizing Works

Images are resized to **fit within** a bounding box. Aspect ratio is always preserved — no stretching or cropping.

| Flags | Geometry | Behavior |
|-------|----------|----------|
| `--max-width 800 --max-height 600` | `800x600` | Fit in 800×600 box |
| `--max-width 800` | `800x` | 800px wide, height auto |
| `--max-height 600` | `x600` | 600px tall, width auto |

Images smaller than the target dimensions are left untouched (no upscaling).

## Options

| Flag | Description |
|------|-------------|
| `--input`, `-i` | Input folder **(required)** |
| `--suffix` | Suffix before extension, e.g. `_opt` → `photo_opt.jpg`. Use `""` for no rename. **(required)** |
| `--max-width` | Max width in pixels |
| `--max-height` | Max height in pixels |
| `--recursive` | Process subfolders |
| `--extensions` | Comma-separated extensions (default: `jpg,jpeg,png,webp,avif,tif,tiff,bmp,gif`) |
| `--quality` | JPEG/WebP compression quality (1–100) |
| `--strip` | Strip metadata (EXIF, ICC profiles) |
| `--sharpen` | Sharpen after resize, e.g. `"0x1"` |
| `--output-dir` | Write output to separate directory (preserves subfolder structure) |
| `--format` | Convert to format, e.g. `webp`, `jpg`, `png` |
| `--overwrite` | Overwrite existing output files |
| `--dry-run` | Print commands without running |
| `--magick-path` | Path to `magick.exe` if not in PATH |
| `--version` | Print version and exit |

At least one of `--max-width` or `--max-height` is required.

## Output Naming

```
Input:  photo.jpg                     Input:  photo.png
Suffix: _resized                      Suffix: _opt  +  Format: webp
Output: photo_resized.jpg             Output: photo_opt.webp
```

With `--output-dir`, subfolder structure is preserved relative to input.

### Skip Logic

Files are skipped (not processed) when:
1. Filename already ends with the suffix
2. Output file already exists (and `--overwrite` not set)
3. Extension not in the allowed list

## Output Summary

```
Done
Geometry: 1920x
Scanned: 147          Processed: 142
Skipped (suffix): 0   Skipped (existing): 3
Skipped (extension): 2   Errors: 0
Elapsed: 12.34s
```

Errors are per-file — a corrupt image won't stop the batch.

## Architecture

```
optimizer.py  →  entry point, delegates to cli.main()
cli.py        →  argparse CLI, validation, output summary
core.py       →  pure logic, no argparse dependency, returns stats dict
```

## Development

```bash
pip install -r requirements-dev.txt
pytest
```

## Full Documentation

See [docs/usage-guide.md](docs/usage-guide.md) for detailed workflows, deep dives on each flag, FAQ, and the `core.process_images()` API reference.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
