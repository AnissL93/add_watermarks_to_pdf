# PDF Watermark Script — Design Spec

**Date:** 2026-03-17
**Status:** Approved

## Overview

A single Python script (`add_watermarks.py`) that adds a configurable watermark text to one or more PDF files, producing two watermarked variants per file (diagonal and tiled) without modifying the originals. The input PDF(s) and watermark text are provided as command-line arguments.

## Requirements

- **CLI parameters:**
  - One or more PDF file paths (positional arguments); if none are given, fall back to processing all `*.pdf` files directly in the script's directory (non-recursive).
  - `--text` / `-t`: watermark text string (default: `"FOR RENTING ONLY"`).
- Originals are never modified.
- Two output variants per PDF:
  - **Diagonal**: large semi-transparent text centered and rotated 45° across each page.
  - **Tiled**: smaller semi-transparent text repeated in a grid across each page, also rotated 45°, starting from the bottom-left corner of the page.
- Output files saved relative to each input file's directory:
  - `<input-dir>/watermarked/diagonal/<original-stem>_diagonal.pdf`
  - `<input-dir>/watermarked/tiled/<original-stem>_tiled.pdf`
- Output subdirectories are excluded from the directory-scan fallback.
- If an output file already exists, it is silently overwritten.

## Tech Stack

- **Python 3**
- **`pypdf`** — merge watermark overlay onto each page of existing PDFs.
- **`reportlab`** — generate the watermark overlay PDF in memory. Uses the built-in Helvetica font (no external font files required).

## Architecture

### Components

1. **`make_diagonal_watermark(width_pt, height_pt, text) -> BytesIO`**
   Uses reportlab to draw `text` once, centered on the page (coordinates in PDF points), rotated 45°, 60pt Helvetica, semi-transparent gray (alpha 0.25). Returns an in-memory PDF.

2. **`make_tiled_watermark(width_pt, height_pt, text) -> BytesIO`**
   Uses reportlab to draw `text` in a repeating grid (spacing: 180pt horizontal, 120pt vertical), starting from the bottom-left origin of the page, each instance rotated 45°, 20pt Helvetica, semi-transparent gray (alpha 0.25). Returns an in-memory PDF.

3. **`watermark_pdf(input_path, wm_func, output_path, text)`**
   Opens the source PDF with pypdf. For each page, reads the page's width and height in PDF points, calls `wm_func(width_pt, height_pt, text)` to generate a correctly-sized overlay, merges the overlay onto the page. Writes the result to `output_path`.
   - If the PDF is encrypted or any page fails to merge, logs a warning to stderr and skips that file entirely; any partial output file is deleted.

4. **`main()`**
   - Parses CLI arguments: optional list of PDF paths and optional `--text` flag (default: `"FOR RENTING ONLY"`).
   - If no PDF paths given, collects all `*.pdf` files directly in the script's directory (non-recursive), excluding files under `watermarked/`.
   - Creates output subdirectories relative to each input file's parent directory.
   - For each input PDF, calls `watermark_pdf` twice (diagonal and tiled) passing the resolved text.
   - Logs progress and any skipped files to stdout/stderr respectively.

### Data Flow

```
*.pdf (script directory, non-recursive, excluding watermarked/)
  └─> watermark_pdf(make_diagonal_watermark) -> watermarked/diagonal/*_diagonal.pdf
  └─> watermark_pdf(make_tiled_watermark)    -> watermarked/tiled/*_tiled.pdf
```

## Error Handling

| Scenario | Behaviour |
|---|---|
| PDF fails to open | Log warning to stderr, skip file, continue. |
| PDF is encrypted / merge fails mid-page | Log warning to stderr, delete partial output, skip file, continue. |
| Output directory cannot be created | Raise and exit with non-zero code. |
| Two input PDFs with the same stem | Last one processed overwrites the earlier output (acceptable for this use case where filenames in the directory are unique). |

## Usage

```bash
pip install pypdf reportlab

# Process all PDFs in the script's directory with default text
python add_watermarks.py

# Process specific files
python add_watermarks.py file1.pdf file2.pdf

# Custom watermark text
python add_watermarks.py --text "CONFIDENTIAL" file1.pdf

# Specific files + custom text
python add_watermarks.py -t "FOR RENTING ONLY" *.pdf
```
