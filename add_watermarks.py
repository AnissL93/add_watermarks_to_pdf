#!/usr/bin/env python3
"""Add diagonal or tiled watermarks to PDF files."""

import argparse
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
