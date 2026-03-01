"""Temp directory and zip helpers for PDF converter outputs."""

import shutil
import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def temp_output_dir():
    """Create a temporary directory; clean it up when done."""
    path = Path(tempfile.mkdtemp(prefix="pdf_convert_"))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def zip_directory(source_dir: Path, zip_path: Path) -> Path:
    """Create a zip file from the contents of a directory. Returns zip_path."""
    source_dir = Path(source_dir)
    zip_path = Path(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in source_dir.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(source_dir))
    return zip_path
