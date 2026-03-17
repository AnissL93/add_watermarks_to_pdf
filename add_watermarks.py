#!/usr/bin/env python3
"""Add diagonal or tiled watermarks to PDF files."""

from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color


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
