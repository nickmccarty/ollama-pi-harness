"""
ocr.py — OCR preprocessing fallback for scanned/image-heavy PDFs.

Cascade:
  1. MarkItDown (pdfminer) — current default; caller already runs this
  2. PyMuPDF (fitz) — better two-column / complex-layout extraction
  3. Vision model (llama3.2-vision via Ollama) — for truly scanned pages

Integration point: agent.py read_file_context() calls is_sparse() after
MarkItDown conversion; if sparse, calls ocr_pdf() for a better extraction.

Usage (module):
    from ocr import is_sparse, ocr_pdf
    content = markitdown_result.text_content or ""
    if is_sparse(content, pdf_path):
        content = ocr_pdf(pdf_path, task=task)

Usage (standalone smoke test):
    python ocr.py <path/to/paper.pdf>
"""

import base64
import io
import os
import sys

# ---------------------------------------------------------------------------
# Availability guards
# ---------------------------------------------------------------------------

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# Vision model (llama3.2-vision via Ollama) — already in the harness
VISION_MODEL = "llama3.2-vision"

# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

# Average chars-per-page threshold: below this after MarkItDown suggests
# the PDF is scanned or heavily image-based (typical arxiv paper: ~3000/page)
SPARSE_CHARS_PER_PAGE = 300

# Absolute floor: even a 1-page paper should yield at least this many chars
SPARSE_ABSOLUTE_FLOOR = 200


def _estimate_page_count(pdf_path: str) -> int:
    """Quick page count via PyMuPDF if available, else rough heuristic from file size."""
    if PYMUPDF_AVAILABLE:
        try:
            with fitz.open(pdf_path) as doc:
                return len(doc)
        except Exception:
            pass
    # Fallback: 1 page per ~10KB is a rough heuristic for text PDFs
    try:
        size = os.path.getsize(pdf_path)
        return max(1, size // 10_000)
    except OSError:
        return 1


def is_sparse(content: str, pdf_path: str) -> bool:
    """
    Return True if the MarkItDown output looks too sparse to be a good extraction.
    Used to decide whether to attempt OCR fallback.
    """
    chars = len(content.strip())
    if chars < SPARSE_ABSOLUTE_FLOOR:
        return True
    pages = _estimate_page_count(pdf_path)
    return (chars / pages) < SPARSE_CHARS_PER_PAGE


# ---------------------------------------------------------------------------
# Backend 1: PyMuPDF text extraction
# ---------------------------------------------------------------------------

MAX_PAGES = 30   # cap to avoid extremely long runs on large documents


def _extract_pymupdf(pdf_path: str) -> str:
    """
    Extract text from a PDF using PyMuPDF.

    Uses get_text("markdown") which handles:
    - Multi-column layout (reads columns left-to-right, not line-by-line)
    - Bold / italic preservation as markdown
    - Table detection
    Falls back to get_text("text") if markdown mode fails.
    """
    doc = fitz.open(pdf_path)
    pages = list(doc)[:MAX_PAGES]
    blocks = []
    for i, page in enumerate(pages, 1):
        try:
            text = page.get_text("markdown")
        except Exception:
            text = page.get_text("text")
        text = text.strip()
        if text:
            blocks.append(text)
    doc.close()
    return "\n\n".join(blocks)


# ---------------------------------------------------------------------------
# Backend 2: Vision model OCR
# ---------------------------------------------------------------------------

OCR_DPI = 150           # render resolution — 150 dpi is fast and readable
MAX_OCR_PAGES = 10      # cap pages sent to the vision model (expensive)

OCR_PROMPT = """\
This is page {page_num} of a research paper PDF. Extract all text content as clean markdown.
Preserve: section headings (## level), paragraph structure, bullet lists, code/math blocks.
Output ONLY the extracted text — no commentary, no page number header."""


def _page_to_b64(page) -> str:
    """Render a PyMuPDF page to a base64-encoded PNG."""
    mat = fitz.Matrix(OCR_DPI / 72, OCR_DPI / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
    return base64.b64encode(pix.tobytes("png")).decode("utf-8")


def _extract_vision(pdf_path: str, task: str = "") -> str:
    """
    OCR a PDF by rendering each page to an image and sending to llama3.2-vision.
    Used as last-resort fallback when PyMuPDF also yields sparse output.
    """
    import inference as _inf

    if not PYMUPDF_AVAILABLE:
        return ""

    doc = fitz.open(pdf_path)
    pages = list(doc)[:MAX_OCR_PAGES]
    blocks = []

    task_hint = f"\nTask context: {task[:200]}" if task else ""

    for i, page in enumerate(pages, 1):
        print(f"    [ocr:vision] page {i}/{len(pages)}...")
        b64 = _page_to_b64(page)
        prompt = OCR_PROMPT.format(page_num=i) + task_hint
        try:
            response = _inf.chat(
                model=VISION_MODEL,
                messages=[{
                    "role": "user",
                    "content": prompt,
                    "images": [b64],
                }],
                options={"temperature": 0.0},
            )
            text = response["message"]["content"].strip()
            if text:
                blocks.append(text)
        except Exception as e:
            print(f"    [ocr:vision] page {i} failed: {e}")

    doc.close()
    return "\n\n".join(blocks)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ocr_pdf(pdf_path: str, task: str = "", markitdown_content: str = "") -> str:
    """
    Attempt a better text extraction from a PDF that MarkItDown rendered sparsely.

    Cascade:
      1. PyMuPDF — fast, handles multi-column layouts well
      2. Vision model — for truly scanned / image-only pages

    Returns the best extraction found, or the original markitdown_content
    if all backends fail or produce no improvement.
    """
    expanded = os.path.expanduser(pdf_path)
    basename = os.path.basename(expanded)

    # --- Stage 1: PyMuPDF ---
    if PYMUPDF_AVAILABLE:
        try:
            pymupdf_text = _extract_pymupdf(expanded)
            if pymupdf_text and not is_sparse(pymupdf_text, expanded):
                print(f"  [ocr:pymupdf] {basename} → {len(pymupdf_text)} chars")
                return pymupdf_text
            # PyMuPDF got something but still sparse — try vision if markedly better
            if pymupdf_text and len(pymupdf_text) > len(markitdown_content) * 1.5:
                print(f"  [ocr:pymupdf] {basename} → {len(pymupdf_text)} chars (partial improvement)")
                return pymupdf_text
            print(f"  [ocr:pymupdf] {basename} still sparse ({len(pymupdf_text)} chars) — trying vision")
        except Exception as e:
            print(f"  [ocr:pymupdf] {basename} failed: {e} — trying vision")
    else:
        print(f"  [ocr] PyMuPDF not available — trying vision")

    # --- Stage 2: Vision model ---
    print(f"  [ocr:vision] sending {min(MAX_OCR_PAGES, _estimate_page_count(expanded))} page(s) to {VISION_MODEL}...")
    vision_text = _extract_vision(expanded, task=task)
    if vision_text and len(vision_text) > len(markitdown_content):
        print(f"  [ocr:vision] {basename} → {len(vision_text)} chars")
        return vision_text

    # All backends failed or produced no improvement — return original
    print(f"  [ocr] all backends failed for {basename} — using original MarkItDown output")
    return markitdown_content


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python ocr.py <path/to/paper.pdf> [task description]")
        sys.exit(1)

    path = sys.argv[1]
    task_desc = sys.argv[2] if len(sys.argv) > 2 else ""

    print(f"[ocr] testing on: {path}")
    print(f"[ocr] PyMuPDF available: {PYMUPDF_AVAILABLE}")

    # Simulate MarkItDown baseline
    try:
        from markitdown import MarkItDown
        md = MarkItDown(enable_plugins=False)
        baseline = md.convert(os.path.expanduser(path)).text_content or ""
        print(f"[ocr] MarkItDown baseline: {len(baseline)} chars")
        sparse = is_sparse(baseline, path)
        print(f"[ocr] sparse={sparse}")
    except Exception as e:
        baseline = ""
        sparse = True
        print(f"[ocr] MarkItDown failed: {e}")

    if sparse:
        result = ocr_pdf(path, task=task_desc, markitdown_content=baseline)
        print(f"\n[ocr] final result: {len(result)} chars")
        print("\n--- first 1000 chars ---")
        print(result[:1000])
    else:
        print("[ocr] not sparse — OCR not needed")
        print(baseline[:500])
