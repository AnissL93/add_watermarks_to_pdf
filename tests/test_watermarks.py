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
