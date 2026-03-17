# Add Watermarks to PDFs

Add diagonal or tiled watermarks to PDF files.

## Installation

```bash
pip install reportlab pypdf
```

## Usage

```bash
python add_watermarks.py [--text "YOUR TEXT"] [pdf1.pdf] [pdf2.pdf] ...
```

### Options

- `--text`, `-t` : Watermark text (default: "FOR RENTING ONLY")
- `PDF`          : Specific PDF file(s) to watermark. If omitted, processes all PDFs in the script's directory.

### Output

Watermarked PDFs are saved to a `watermarked/` subdirectory:
- `watermarked/diagonal/` — Single centered diagonal watermark
- `watermarked/tiled/` — Tiled watermark repeated across each page

### Examples

```bash
# Use default text on all PDFs in current directory
python add_watermarks.py

# Custom watermark text
python add_watermarks.py --text "CONFIDENTIAL" document.pdf

# Multiple files
python add_watermarks.py file1.pdf file2.pdf file3.pdf
```
