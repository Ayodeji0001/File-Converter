"""Convert PDF to text, images, DOCX, Markdown, SVG, and HTML."""

import tempfile
from pathlib import Path

import pymupdf
from pdf2docx import Converter

from utils import temp_output_dir, zip_directory


def convert_to_text(pdf_path: Path) -> Path:
    """Extract plain text from PDF. Returns path to .txt file."""
    pdf_path = Path(pdf_path)
    out_path = Path(tempfile.gettempdir()) / f"pdf_convert_{pdf_path.stem}.txt"
    doc = pymupdf.open(pdf_path)
    try:
        parts = [doc[i].get_text("text") for i in range(len(doc))]
        out_path.write_text("\n\n".join(parts), encoding="utf-8")
        return out_path
    finally:
        doc.close()


def convert_to_images(
    pdf_path: Path, dpi: int = 150, image_fmt: str = "png"
) -> Path:
    """Render each page as an image. Returns path to .zip containing images."""
    pdf_path = Path(pdf_path)
    with temp_output_dir() as tmp:
        doc = pymupdf.open(pdf_path)
        try:
            for i in range(len(doc)):
                pix = doc[i].get_pixmap(dpi=dpi)
                ext = "png" if image_fmt.lower() == "png" else "jpg"
                path = tmp / f"page_{i + 1:04d}.{ext}"
                pix.save(str(path))
        finally:
            doc.close()
        zip_path = Path(tempfile.gettempdir()) / f"pdf_convert_{pdf_path.stem}_images.zip"
        return zip_directory(tmp, zip_path)


def convert_to_docx(pdf_path: Path) -> Path:
    """Convert PDF to DOCX. Returns path to .docx file."""
    pdf_path = Path(pdf_path)
    out_path = Path(tempfile.gettempdir()) / f"pdf_convert_{pdf_path.stem}.docx"
    cv = Converter(str(pdf_path))
    try:
        cv.convert(str(out_path))
        return out_path
    finally:
        cv.close()


def convert_to_markdown(pdf_path: Path) -> Path:
    """Convert PDF to Markdown via pymupdf4llm. Returns path to .md file."""
    import pymupdf4llm

    pdf_path = Path(pdf_path)
    out_path = Path(tempfile.gettempdir()) / f"pdf_convert_{pdf_path.stem}.md"
    md_text = pymupdf4llm.to_markdown(str(pdf_path))
    out_path.write_bytes(md_text.encode("utf-8"))
    return out_path


def convert_to_svg(pdf_path: Path) -> Path:
    """Export each page as SVG. Returns path to .zip containing SVGs."""
    pdf_path = Path(pdf_path)
    with temp_output_dir() as tmp:
        doc = pymupdf.open(pdf_path)
        try:
            for i in range(len(doc)):
                svg_content = doc[i].get_svg_image()
                path = tmp / f"page_{i + 1:04d}.svg"
                path.write_text(svg_content, encoding="utf-8")
        finally:
            doc.close()
        zip_path = Path(tempfile.gettempdir()) / f"pdf_convert_{pdf_path.stem}_svg.zip"
        return zip_directory(tmp, zip_path)


def convert_to_html(pdf_path: Path) -> Path:
    """Extract HTML from each page and save as one .html file. Returns path to .html."""
    pdf_path = Path(pdf_path)
    out_path = Path(tempfile.gettempdir()) / f"pdf_convert_{pdf_path.stem}.html"
    doc = pymupdf.open(pdf_path)
    try:
        parts = [doc[i].get_text("html") for i in range(len(doc))]
        body = "\n".join(parts)
        html = f'<!DOCTYPE html>\n<html><head><meta charset="utf-8"/><title>{pdf_path.stem}</title></head><body>\n{body}\n</body></html>'
        out_path.write_text(html, encoding="utf-8")
        return out_path
    finally:
        doc.close()
