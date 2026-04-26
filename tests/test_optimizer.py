import sys
from pathlib import Path
import subprocess
import shutil
import builtins
import pytest

import optimizer


def test_parse_extensions_valid():
    assert optimizer.parse_extensions("jpg,png") == {"jpg", "png"}
    assert optimizer.parse_extensions(".JPG, .Png ") == {"jpg", "png"}


def test_parse_extensions_empty():
    with pytest.raises(Exception):
        optimizer.parse_extensions("")


@pytest.mark.parametrize(
    "max_w,max_h,expected",
    [
        (1920, 1080, "1920x1080"),
        (1920, None, "1920x"),
        (None, 1080, "x1080"),
    ],
)
def test_build_geometry(max_w, max_h, expected):
    assert optimizer.build_geometry(max_w, max_h) == expected


def test_resolve_magick_with_override(tmp_path, monkeypatch):
    f = tmp_path / "magick.exe"
    f.write_text("x")
    assert optimizer.resolve_magick(str(f)) == str(f)


def test_resolve_magick_in_path(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "C:\\magick")
    assert optimizer.resolve_magick(None) == "C:\\magick"


def test_resolve_magick_falls_back_to_convert(monkeypatch):
    def mock_which(name):
        return {"magick": None, "convert": "/usr/bin/convert"}.get(name)

    monkeypatch.setattr(shutil, "which", mock_which)
    assert optimizer.resolve_magick(None) == "/usr/bin/convert"


def test_resolve_magick_missing(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: None)
    with pytest.raises(SystemExit):
        optimizer.resolve_magick(None)


def test_cli_dry_run(tmp_path, monkeypatch, capsys):
    # create a few files
    d = tmp_path / "imgs"
    d.mkdir()
    (d / "a.jpg").write_text("x")
    (d / "b.png").write_text("x")
    # ensure magick is found
    monkeypatch.setattr(shutil, "which", lambda name: "magick")

    sys_argv = [
        "optimizer.py",
        "--input",
        str(d),
        "--suffix",
        "_res",
        "--max-width",
        "100",
        "--dry-run",
    ]
    monkeypatch.setattr(sys, "argv", sys_argv)
    optimizer.main()
    captured = capsys.readouterr()
    assert "DRY-RUN:" in captured.out
