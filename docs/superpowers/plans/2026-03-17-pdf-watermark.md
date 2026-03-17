# PDF Watermark Script Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write a single Python script that stamps a configurable watermark text onto every page of one or more PDFs, producing two output variants (diagonal and tiled) per file.

**Architecture:** A single `add_watermarks.py` script with three pure functions (`make_diagonal_watermark`, `make_tiled_watermark`, `watermark_pdf`) and a `main()` that wires CLI args to those functions. Watermark overlays are generated in-memory with reportlab and merged onto original pages with pypdf. Originals are never modified; outputs go into `watermarked/diagonal/` and `watermarked/tiled/` subdirectories relative to each input file.

**Tech Stack:** Python 3, `pypdf`, `reportlab`

---

## File Structure

| Path | Role |
|------|------|
| `add_watermarks.py` | Main script — CLI entry point + all watermark logic |
| `tests/test_watermarks.py` | Pytest unit + integration tests |

---

### Task 1: Project scaffold & dependencies

**Files:**
- Create: `requirements.txt`
- Create: `tests/__init__.py`
- Create: `tests/test_watermarks.py` (empty stub)

- [ ] **Step 1: Create `requirements.txt`**

```
pypdf>=4.0.0
reportlab>=4.0.0
pytest>=8.0.0
```

- [ ] **Step 2: Create `.gitignore`**

```
watermarked/
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: packages install without error.

- [ ] **Step 4: Create empty test file**

```python
# tests/test_watermarks.py
```

- [ ] **Step 5: Create `tests/__init__.py`**

Empty file.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .gitignore tests/
git commit -m "chore: add dependencies, gitignore, and test scaffold"
```

---

### Task 2: `make_diagonal_watermark`

**Files:**
- Create: `add_watermarks.py` (initial skeleton)
- Modify: `tests/test_watermarks.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_watermarks.py
import pytest
from io import BytesIO
from pypdf import PdfReader


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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_watermarks.py::test_make_diagonal_watermark_returns_valid_pdf -v
```

Expected: `ImportError` — `add_watermarks` not found.

- [ ] **Step 3: Create `add_watermarks.py` with the function**

```python
#!/usr/bin/env python3
"""Add diagonal or tiled watermarks to PDF files."""

import sys
import argparse
from io import BytesIO
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from pypdf import PdfReader, PdfWriter


def make_diagonal_watermark(width_pt: float, height_pt: float, text: str) -> BytesIO:
    """Return a single-page in-memory PDF with `text` as a centered diagonal watermark."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(width_pt, height_pt))
    c.setFillColor(Color(0.5, 0.5, 0.5, alpha=0.25))
    c.setFont("Helvetica", 60)
    c.saveState()
    c.translate(width_pt / 2, height_pt / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    c.save()
    buf.seek(0)
    return buf
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_watermarks.py -k "diagonal" -v
```

Expected: 2 PASSED.

- [ ] **Step 5: Commit**

```bash
git add add_watermarks.py tests/test_watermarks.py
git commit -m "feat: add make_diagonal_watermark"
```

---

### Task 3: `make_tiled_watermark`

**Files:**
- Modify: `add_watermarks.py`
- Modify: `tests/test_watermarks.py`

- [ ] **Step 1: Write the failing tests**

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_watermarks.py -k "tiled" -v
```

Expected: `ImportError` for `make_tiled_watermark`.

- [ ] **Step 3: Add `make_tiled_watermark` to `add_watermarks.py`**

Add after `make_diagonal_watermark`:

```python
def make_tiled_watermark(width_pt: float, height_pt: float, text: str) -> BytesIO:
    """Return a single-page in-memory PDF with `text` tiled across the page."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(width_pt, height_pt))
    c.setFillColor(Color(0.5, 0.5, 0.5, alpha=0.25))
    c.setFont("Helvetica", 20)
    x_spacing = 180
    y_spacing = 120
    x = 0.0
    while x < width_pt + x_spacing:
        y = 0.0
        while y < height_pt + y_spacing:
            c.saveState()
            c.translate(x, y)
            c.rotate(45)
            c.drawCentredString(0, 0, text)
            c.restoreState()
            y += y_spacing
        x += x_spacing
    c.save()
    buf.seek(0)
    return buf
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_watermarks.py -k "tiled" -v
```

Expected: 2 PASSED.

- [ ] **Step 5: Commit**

```bash
git add add_watermarks.py tests/test_watermarks.py
git commit -m "feat: add make_tiled_watermark"
```

---

### Task 4: `watermark_pdf`

**Files:**
- Modify: `add_watermarks.py`
- Modify: `tests/test_watermarks.py`

- [ ] **Step 1: Write the failing tests**

```python
import tempfile
import os


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
    import unittest.mock as mock

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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_watermarks.py -k "watermark_pdf" -v
```

Expected: `ImportError` for `watermark_pdf`.

- [ ] **Step 3: Add `watermark_pdf` to `add_watermarks.py`**

Add after `make_tiled_watermark`:

```python
def watermark_pdf(
    input_path: Path,
    wm_func,
    output_path: Path,
    text: str,
) -> None:
    """Merge a watermark overlay onto every page of `input_path`, write to `output_path`."""
    try:
        reader = PdfReader(input_path)
    except Exception as exc:
        print(f"WARNING: could not open {input_path}: {exc}", file=sys.stderr)
        return

    writer = PdfWriter()
    try:
        for page in reader.pages:
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            wm_buf = wm_func(width, height, text)
            wm_page = PdfReader(wm_buf).pages[0]
            page.merge_page(wm_page)
            writer.add_page(page)
    except Exception as exc:
        print(f"WARNING: failed to watermark {input_path}: {exc}", file=sys.stderr)
        if output_path.exists():
            output_path.unlink()
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_watermarks.py -k "watermark_pdf" -v
```

Expected: 4 PASSED.

- [ ] **Step 5: Commit**

```bash
git add add_watermarks.py tests/test_watermarks.py
git commit -m "feat: add watermark_pdf"
```

---

### Task 5: `main()` — CLI wiring

**Files:**
- Modify: `add_watermarks.py`
- Modify: `tests/test_watermarks.py`

- [ ] **Step 1: Write the failing tests**

```python
import subprocess


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
        import shutil
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_watermarks.py -k "main_cli" -v
```

Expected: tests fail (no `main` or no CLI support).

- [ ] **Step 3: Add `main()` and `__main__` block to `add_watermarks.py`**

Add at the bottom of the file:

```python
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add watermarks to PDF files."
    )
    parser.add_argument(
        "pdfs",
        nargs="*",
        metavar="PDF",
        help="PDF file(s) to watermark. Defaults to all *.pdf in the script's directory.",
    )
    parser.add_argument(
        "--text", "-t",
        default="FOR RENTING ONLY",
        help='Watermark text (default: "FOR RENTING ONLY")',
    )
    args = parser.parse_args()

    if args.pdfs:
        input_paths = [Path(p) for p in args.pdfs]
    else:
        script_dir = Path(__file__).parent
        watermarked_dir = script_dir / "watermarked"
        input_paths = [
            p for p in script_dir.glob("*.pdf")
            if not p.resolve().is_relative_to(watermarked_dir.resolve())
        ]

    if not input_paths:
        print("No PDF files found.", file=sys.stderr)
        sys.exit(0)

    for src in input_paths:
        src = Path(src).resolve()
        out_base = src.parent / "watermarked"
        diagonal_out = out_base / "diagonal" / f"{src.stem}_diagonal.pdf"
        tiled_out = out_base / "tiled" / f"{src.stem}_tiled.pdf"

        print(f"Processing: {src.name}")
        watermark_pdf(src, make_diagonal_watermark, diagonal_out, args.text)
        watermark_pdf(src, make_tiled_watermark, tiled_out, args.text)

    print("Done.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all tests**

```bash
pytest tests/test_watermarks.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Smoke test against real files**

```bash
python add_watermarks.py
```

Expected: prints `Processing: <filename>` for each PDF, creates `watermarked/diagonal/` and `watermarked/tiled/` with watermarked copies.

- [ ] **Step 6: Commit**

```bash
git add add_watermarks.py tests/test_watermarks.py
git commit -m "feat: add CLI main() with --text parameter and file args"
```

---

### Task 6: Final check

- [ ] **Step 1: Run full test suite**

```bash
pytest tests/ -v
```

Expected: all tests PASS, no warnings.

- [ ] **Step 2: Test custom text via CLI**

```bash
python add_watermarks.py --text "CONFIDENTIAL" driving-license-uk-huiying-lan.pdf
```

Expected: `watermarked/diagonal/driving-license-uk-huiying-lan_diagonal.pdf` and `watermarked/tiled/driving-license-uk-huiying-lan_tiled.pdf` created.

- [ ] **Step 3: Test default (all PDFs, default text)**

```bash
python add_watermarks.py
```

Expected: all 9 PDFs watermarked into both output folders.

- [ ] **Step 4: Final commit**

```bash
git add add_watermarks.py tests/test_watermarks.py
git commit -m "feat: complete PDF watermark script with diagonal and tiled modes"
```
