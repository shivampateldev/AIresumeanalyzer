"""
resume_parser.py — Robust resume text extraction.

Fixed parsing order per spec:
  1. pdfminer.six  (more reliable for modern PDFs, handles fonts better)
  2. PyPDF2        (fallback for older/simpler PDFs)
  3. Error         (print clear message)

Also:
  - Strips quotes from file paths (handles drag-and-drop paths with quotes)
  - Warns when word count < 50 (likely parsing failure)
  - Validates min/max expected word count for a resume
"""
import os
import re
from modules.logger import logger

_MIN_WORDS = 30     # below this = definitely failed parse
_WARN_WORDS = 50    # below this = warn user


class ResumeParser:

    @staticmethod
    def extract_text(input_source: str, is_file: bool = False) -> str:
        if not is_file:
            text = ResumeParser._normalize(input_source)
            ResumeParser._validate_word_count(text, "Pasted text")
            return text

        # Strip surrounding quotes (drag-and-drop on Windows adds them)
        path = input_source.strip().strip('"').strip("'").strip()
        if not os.path.exists(path):
            print(f"  [Parser] File not found: {path}")
            logger.error(f"Resume file not found: {path}")
            return ""

        ext = os.path.splitext(path)[1].lower()

        if ext == ".txt":
            text = ResumeParser._read_txt(path)
        elif ext == ".pdf":
            # pdfminer.six FIRST (better for modern PDFs)
            text = ResumeParser._read_pdf_pdfminer(path)
            word_count = len(text.split()) if text else 0
            if not text.strip() or word_count < _MIN_WORDS:
                logger.warning(
                    f"pdfminer extracted {word_count} words. Trying PyPDF2 fallback..."
                )
                text_pypdf = ResumeParser._read_pdf_pypdf2(path)
                if len(text_pypdf.split()) > word_count:
                    text = text_pypdf
                    logger.info("PyPDF2 produced better result.")
        else:
            print(f"  [Parser] Unsupported file type '{ext}'. Supported: .pdf, .txt")
            return ""

        ResumeParser._validate_word_count(text, path)
        return text

    # ──────────────────────────────────────────────────────────────────────────
    # Readers
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _read_txt(path: str) -> str:
        for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                with open(path, "r", encoding=enc, errors="replace") as f:
                    text = f.read()
                logger.info(f"TXT read OK ({enc}): {len(text)} chars.")
                return ResumeParser._normalize(text)
            except Exception:
                continue
        logger.error(f"Could not read txt file: {path}")
        return ""

    @staticmethod
    def _read_pdf_pdfminer(path: str) -> str:
        """Primary PDF reader — handles complex layouts, embedded fonts."""
        try:
            from pdfminer.high_level import extract_text as pm_extract
            text = pm_extract(path)
            if text:
                logger.info(f"pdfminer OK: {len(text)} chars.")
                return ResumeParser._normalize(text)
            return ""
        except ImportError:
            logger.warning("pdfminer.six not installed. Run: pip install pdfminer.six")
            return ""
        except Exception as e:
            logger.warning(f"pdfminer failed: {e}")
            return ""

    @staticmethod
    def _read_pdf_pypdf2(path: str) -> str:
        """Fallback PDF reader."""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(path)
            pages = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    pages.append(t)
            text = "\n".join(pages)
            logger.info(f"PyPDF2 OK: {len(text)} chars from {len(reader.pages)} page(s).")
            return ResumeParser._normalize(text)
        except ImportError:
            logger.warning("PyPDF2 not installed. Run: pip install PyPDF2")
            return ""
        except Exception as e:
            logger.warning(f"PyPDF2 failed: {e}")
            return ""

    # ──────────────────────────────────────────────────────────────────────────
    # Utilities
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _normalize(text: str) -> str:
        """Fix encoding artifacts and normalize whitespace."""
        if not text:
            return ""
        fixes = {
            "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
            "\u2013": "-", "\u2014": "-", "\ufb01": "fi", "\ufb02": "fl",
            "\u00e2\u0080\u0099": "'", "\xa0": " ", "\x00": "",
        }
        for bad, good in fixes.items():
            text = text.replace(bad, good)
        # Collapse excessive whitespace but keep newlines for structure hints
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def _validate_word_count(text: str, source_label: str) -> None:
        """Warn if word count seems too low for a real resume."""
        wc = len(text.split())
        if wc < _MIN_WORDS:
            print(f"\n  [!] WARNING: Only {wc} words extracted from '{source_label}'.")
            print(f"  [!] PDF parsing may have failed. Try saving your PDF as text first,")
            print(f"  [!] or paste the resume content directly when prompted.\n")
        elif wc < _WARN_WORDS:
            print(f"  [!] WARNING: Only {wc} words extracted. Resume may be incomplete.")
        else:
            print(f"  [Parser] Extracted {wc} words. OK.")
        logger.info(f"Resume word count: {wc}")
