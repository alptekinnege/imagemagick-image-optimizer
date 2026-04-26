# ImageMagick Image Resizer (Python)

Resize images in a folder with ImageMagick. Output files keep the same format and are saved in the same folder with a suffix.

## Requirements
- Python 3.8+
- ImageMagick installed and either `magick` or `convert` available in PATH

## Usage

Basic example:

```
python optimizer.py --input "C:\\path\\to\\images" --suffix "_resized" --max-width 1920 --max-height 1080
```

Only width (height scales proportionally):

```
python optimizer.py --input "C:\\path\\to\\images" --suffix "_resized" --max-width 1920
```

Only height (width scales proportionally):

```
python optimizer.py --input "C:\\path\\to\\images" --suffix "_resized" --max-height 1080
```

## Options
- `--input`, `-i`: Input folder (required)
- `--suffix`: Suffix added before extension (required)
- `--max-width`: Maximum width in pixels
- `--max-height`: Maximum height in pixels
- `--recursive`: Process subfolders
- `--extensions`: Comma-separated list of extensions (default: common image types)
- `--magick-path`: Path to `magick.exe` (or equivalent ImageMagick binary) if not in PATH
- `--overwrite`: Overwrite output files if they exist
- `--dry-run`: Print ImageMagick commands without running them

## Notes
- Output files are written to the same folder as the input file.
- Output format is the same as the input file extension.
- Images are resized proportionally to fit within the max width/height.
- Files whose names already end with the suffix are skipped to avoid reprocessing.
- The tool resolves `magick` first, then falls back to `convert` when `magick` is unavailable.

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Development & Tests
Install dev dependencies and run tests:

```
python -m pip install -r requirements-dev.txt
pytest
```

