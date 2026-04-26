# ImageMagick Image Resizer (Python)

Resize images in a folder with ImageMagick. Output files keep the same format and are saved in the same folder with a suffix.

## Requirements
- Python 3.8+
- ImageMagick installed and `magick` available in PATH

On Ubuntu/Debian, ImageMagick 6 may install the command as `convert` instead of
`magick`. If `magick` is missing, either install an ImageMagick package that
provides it or pass the command path explicitly with `--magick-path`.

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
- `--magick-path`: Path to `magick.exe` if not in PATH
- `--overwrite`: Overwrite output files if they exist
- `--dry-run`: Print ImageMagick commands without running them

## Notes
- Output files are written to the same folder as the input file.
- Output format is the same as the input file extension.
- Images are resized proportionally to fit within the max width/height.
- Files whose names already end with the suffix are skipped to avoid reprocessing.

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Development & Tests
Create a virtual environment, install dev dependencies, and run tests:

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest
```

