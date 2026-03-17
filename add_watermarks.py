#!/usr/bin/env python3
"""Add diagonal or tiled watermarks to PDF files."""

import sys
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
