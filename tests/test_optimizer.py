from pathlib import Path
import subprocess
import shutil
import sys
import argparse
import pytest

import core
import cli


class TestParseExtensions:
    def test_valid(self):
        assert core.parse_extensions("jpg,png") == {"jpg", "png"}

    def test_dots_and_case(self):
        assert core.parse_extensions(".JPG, .Png ") == {"jpg", "png"}

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            core.parse_extensions("")


class TestBuildGeometry:
    @pytest.mark.parametrize(
        "max_w,max_h,expected",
        [
            (1920, 1080, "1920x1080"),
            (1920, None, "1920x"),
            (None, 1080, "x1080"),
        ],
    )
    def test_combinations(self, max_w, max_h, expected):
        assert core.build_geometry(max_w, max_h) == expected


class TestResolveMagick:
    def test_with_override(self, tmp_path):
        f = tmp_path / "magick.exe"
        f.write_text("x")
        assert core.resolve_magick(str(f)) == str(f)

    def test_in_path(self, monkeypatch):
        monkeypatch.setattr(shutil, "which", lambda name: "C:\\magick")
        assert core.resolve_magick(None) == "C:\\magick"

    def test_missing(self, monkeypatch):
        monkeypatch.setattr(shutil, "which", lambda name: None)
        with pytest.raises(SystemExit):
            core.resolve_magick(None)


class TestCLI:
    def test_validate_output_format(self):
        # Valid formats
        assert cli._validate_output_format("jpg") == "jpg"
        assert cli._validate_output_format(".png") == "png"
        assert cli._validate_output_format("tar.gz") == "tar.gz"

        # Invalid formats containing path separators
        with pytest.raises(argparse.ArgumentTypeError, match="must not contain path separators"):
            cli._validate_output_format("a/b")

        with pytest.raises(argparse.ArgumentTypeError, match="must not contain path separators"):
            cli._validate_output_format("../foo")

        with pytest.raises(argparse.ArgumentTypeError, match="must not contain path separators"):
            cli._validate_output_format("\\foo")

        with pytest.raises(argparse.ArgumentTypeError, match="must not contain path separators"):
            cli._validate_output_format("C:\\foo")

    def test_dry_run_integration(self, tmp_path, monkeypatch, capsys):
        d = tmp_path / "imgs"
        d.mkdir()
        (d / "a.jpg").write_text("x")
        (d / "b.png").write_text("x")

        monkeypatch.setattr(shutil, "which", lambda name: "magick")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "optimizer.py",
                "--input", str(d),
                "--suffix", "_res",
                "--max-width", "100",
                "--dry-run",
            ],
        )
        cli.main()
        captured = capsys.readouterr()
        assert "DRY-RUN:" in captured.out

    def test_parser_produces_version_flag(self, monkeypatch, capsys):
        monkeypatch.setattr(
            sys,
            "argv",
            ["optimizer.py", "--version"],
        )
        parser = cli.build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args()


class TestProcessImages:
    def test_dry_run_stats(self, tmp_path, monkeypatch):
        d = tmp_path / "imgs"
        d.mkdir()
        (d / "a.jpg").write_text("x")

        monkeypatch.setattr(shutil, "which", lambda name: "magick")

        stats = core.process_images(
            input_dir=d,
            suffix="_res",
            max_width=100,
            dry_run=True,
        )
        assert stats["total"] == 1
        assert stats["would_process"] == 1
        assert stats["processed"] == 0

    def test_skips_suffix(self, tmp_path, monkeypatch):
        d = tmp_path / "imgs"
        d.mkdir()
        (d / "a_res.jpg").write_text("x")

        monkeypatch.setattr(shutil, "which", lambda name: "magick")

        stats = core.process_images(
            input_dir=d,
            suffix="_res",
            max_width=100,
        )
        assert stats["skipped_suffix"] == 1

    def test_skips_extension(self, tmp_path, monkeypatch):
        d = tmp_path / "imgs"
        d.mkdir()
        (d / "a.txt").write_text("x")

        monkeypatch.setattr(shutil, "which", lambda name: "magick")

        stats = core.process_images(
            input_dir=d,
            suffix="_res",
            max_width=100,
        )
        assert stats["skipped_extension"] == 1

    def test_output_dir_preserves_structure(self, tmp_path, monkeypatch):
        d = tmp_path / "imgs"
        d.mkdir()
        subdir = d / "sub"
        subdir.mkdir()
        (subdir / "a.jpg").write_text("x")

        out_d = tmp_path / "out"

        monkeypatch.setattr(shutil, "which", lambda name: "magick")
        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _FakeResult(0))

        stats = core.process_images(
            input_dir=d,
            suffix="_opt",
            max_width=100,
            recursive=True,
            output_dir=out_d,
        )
        assert stats["total"] == 1
        assert stats["processed"] == 1

    def test_output_format_changes_extension(self, tmp_path, monkeypatch):
        d = tmp_path / "imgs"
        d.mkdir()
        (d / "a.png").write_text("x")

        commands = []
        def capture(*a, **kw):
            commands.append(a[0])
            return _FakeResult(0)

        monkeypatch.setattr(shutil, "which", lambda name: "magick")
        monkeypatch.setattr(subprocess, "run", capture)

        core.process_images(
            input_dir=d,
            suffix="_res",
            max_width=100,
            output_format="webp",
        )
        assert any(".webp" in str(c) for c in commands)

    def test_quality_strip_sharpen_args(self, tmp_path, monkeypatch):
        d = tmp_path / "imgs"
        d.mkdir()
        (d / "a.jpg").write_text("x")

        commands = []
        def capture(*a, **kw):
            commands.append(a[0])
            return _FakeResult(0)

        monkeypatch.setattr(shutil, "which", lambda name: "magick")
        monkeypatch.setattr(subprocess, "run", capture)

        core.process_images(
            input_dir=d,
            suffix="_opt",
            max_width=100,
            quality=80,
            strip=True,
            sharpen="0x1",
        )
        cmd = commands[0]
        assert "-quality" in cmd and "80" in cmd
        assert "-strip" in cmd
        assert "-sharpen" in cmd


class _FakeResult:
    def __init__(self, returncode):
        self.returncode = returncode
        self.stderr = ""
