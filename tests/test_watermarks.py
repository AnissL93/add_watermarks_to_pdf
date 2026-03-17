import pytest
import tempfile
import os
import sys
import subprocess
import shutil
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader, PdfWriter


def test_make_diagonal_watermark_returns_valid_pdf():
    from add_watermarks import make_diagonal_watermark
    buf = make_diagonal_watermark(595, 842, "TEST WATERMARK")
    assert isinstance(buf, BytesIO)
    reader = PdfReader(buf)
    assert len(reader.pages) == 1


def test_make_diagonal_watermark_custom_text():
    from add_watermarks import make_diagonal_watermark
    # Different text strings should both produce a valid single-page PDF
    buf1 = make_diagonal_watermark(595, 842, "FOR RENTING ONLY")
    buf2 = make_diagonal_watermark(595, 842, "CONFIDENTIAL")
    assert PdfReader(buf1).pages[0] is not None
    assert PdfReader(buf2).pages[0] is not None


def test_make_tiled_watermark_returns_valid_pdf():
    from add_watermarks import make_tiled_watermark
    buf = make_tiled_watermark(595, 842, "TEST WATERMARK")
    assert isinstance(buf, BytesIO)
    reader = PdfReader(buf)
    assert len(reader.pages) == 1


def test_make_tiled_watermark_small_page():
    """Even a tiny page should not raise."""
    from add_watermarks import make_tiled_watermark
    buf = make_tiled_watermark(100, 100, "X")
    assert PdfReader(buf).pages[0] is not None


def _make_sample_pdf(path: Path, pages: int = 1):
    """Create a minimal valid PDF at `path` with `pages` pages."""
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)
    with open(path, "wb") as f:
        writer.write(f)


def test_watermark_pdf_diagonal_produces_output():
    from add_watermarks import watermark_pdf, make_diagonal_watermark
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "sample.pdf"
        dst = Path(tmpdir) / "sample_diagonal.pdf"
        _make_sample_pdf(src)
        watermark_pdf(src, make_diagonal_watermark, dst, "FOR RENTING ONLY")
        assert dst.exists()
        assert dst.stat().st_size > 0
        reader = PdfReader(dst)
        assert len(reader.pages) == 1


def test_watermark_pdf_multipage():
    from add_watermarks import watermark_pdf, make_tiled_watermark
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "multi.pdf"
        dst = Path(tmpdir) / "multi_tiled.pdf"
        _make_sample_pdf(src, pages=3)
        watermark_pdf(src, make_tiled_watermark, dst, "TEST")
        reader = PdfReader(dst)
        assert len(reader.pages) == 3


def test_watermark_pdf_bad_input_skips_gracefully(capsys):
    from add_watermarks import watermark_pdf, make_diagonal_watermark
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "nonexistent.pdf"
        dst = Path(tmpdir) / "out.pdf"
        # Should not raise; should log to stderr
        watermark_pdf(src, make_diagonal_watermark, dst, "X")
        captured = capsys.readouterr()
        assert "WARNING" in captured.err or "warning" in captured.err.lower()
        assert not dst.exists()


def test_watermark_pdf_partial_output_deleted_on_merge_failure(capsys, tmp_path):
    """If merging fails mid-way, any partial output file must be deleted."""
    from add_watermarks import watermark_pdf

    src = tmp_path / "sample.pdf"
    dst = tmp_path / "out.pdf"
    _make_sample_pdf(src, pages=2)

    # Create a pre-existing stale output to confirm it gets cleaned up
    dst.write_bytes(b"stale")

    def failing_wm(w, h, t):
        raise RuntimeError("simulated merge failure")

    watermark_pdf(src, failing_wm, dst, "X")
    captured = capsys.readouterr()
    assert "WARNING" in captured.err or "warning" in captured.err.lower()
    assert not dst.exists(), "partial output must be deleted on failure"


def test_main_cli_no_args_scans_script_directory():
    """Integration: with no args, script processes all *.pdf in its own directory,
    excluding files already in watermarked/ subdirectories."""
    script = Path(__file__).parent.parent / "add_watermarks.py"
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        _make_sample_pdf(tmpdir / "a.pdf")
        _make_sample_pdf(tmpdir / "b.pdf")
        # Pre-create a watermarked output to confirm it is NOT re-processed
        wm_dir = tmpdir / "watermarked" / "diagonal"
        wm_dir.mkdir(parents=True)
        _make_sample_pdf(wm_dir / "a_diagonal.pdf")

        # Copy script temporarily into tmpdir so __file__ resolves there
        script_copy = tmpdir / "add_watermarks.py"
        shutil.copy(script, script_copy)

        result = subprocess.run(
            [sys.executable, str(script_copy)],
            capture_output=True, text=True, cwd=str(tmpdir)
        )
        assert result.returncode == 0, result.stderr
        assert (tmpdir / "watermarked" / "diagonal" / "a_diagonal.pdf").exists()
        assert (tmpdir / "watermarked" / "diagonal" / "b_diagonal.pdf").exists()
        assert (tmpdir / "watermarked" / "tiled" / "a_tiled.pdf").exists()
        assert (tmpdir / "watermarked" / "tiled" / "b_tiled.pdf").exists()
        # The pre-existing watermarked PDF should not produce a double-watermarked copy
        assert not (tmpdir / "watermarked" / "diagonal" / "a_diagonal_diagonal.pdf").exists()


def test_main_cli_specific_files():
    """Integration: run the script as a subprocess with explicit file args."""
    script = Path(__file__).parent.parent / "add_watermarks.py"
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        src = tmpdir / "sample.pdf"
        _make_sample_pdf(src)
        result = subprocess.run(
            [sys.executable, str(script), str(src), "--text", "TESTING"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, result.stderr
        assert (tmpdir / "watermarked" / "diagonal" / "sample_diagonal.pdf").exists()
        assert (tmpdir / "watermarked" / "tiled" / "sample_tiled.pdf").exists()


def test_main_cli_default_text():
    """Integration: default text is used when --text not supplied."""
    script = Path(__file__).parent.parent / "add_watermarks.py"
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        src = tmpdir / "doc.pdf"
        _make_sample_pdf(src)
        result = subprocess.run(
            [sys.executable, str(script), str(src)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, result.stderr
        assert (tmpdir / "watermarked" / "diagonal" / "doc_diagonal.pdf").exists()
        assert (tmpdir / "watermarked" / "tiled" / "doc_tiled.pdf").exists()
