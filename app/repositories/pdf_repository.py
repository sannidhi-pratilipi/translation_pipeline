from PyPDF2 import PdfReader
import re

class PDFRepository:
    def _load_with_pypdf2(self, path: str) -> str:
        """Try to extract text using PyPDF2. Returns empty string on failure."""
        try:
            reader = PdfReader(path)
        except Exception:
            return ""

        text_parts: list[str] = []
        for page in reader.pages:
            try:
                page_text = page.extract_text()
            except Exception:
                page_text = None

            if page_text:
                text_parts.append(page_text)

        return "\n".join(text_parts).strip()

    def _load_with_pdfminer(self, path: str) -> str:
        """Fallback to pdfminer.six for more robust extraction, if installed."""
        try:
            from pdfminer.high_level import extract_text  
        except ImportError:
            raise RuntimeError(
                "No text could be extracted from PDF and pdfminer.six is not installed. "
                "Install it with `pip install pdfminer.six` for better PDF text extraction."
            )

        try:
            text = extract_text(path) or ""
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF with pdfminer.six: {e}")

        text = text.strip()
        if not text:
            raise RuntimeError(
                "No text could be extracted from the PDF, even with pdfminer.six. "
                "The file is likely scanned images without an embedded text layer."
            )

        return text
    
    def load_text(self, path: str) -> str:
        text = self._load_with_pdfminer(path)
        if not text:
            text = self._load_with_pypdf2(path)

        return self._normalize_extracted_text(text)
    
    # def _normalize_extracted_text(self, text: str) -> str:
    #     """
    #     Normalize broken PDF line wrapping.

    #     - Merge single line breaks into spaces
    #     - Preserve true paragraph breaks
    #     - Clean excessive whitespace
    #     """

    #     if not text:
    #         return ""
    #     text = text.replace("\r\n", "\n")
    #     # Keep double newlines as paragraph separators
    #     text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    #     text = re.sub(r'[ \t]+', ' ', text)
    #     text = re.sub(r'\n{3,}', '\n\n', text)

    #     return text.strip()

    def _normalize_extracted_text(self, text: str) -> str:
        """
        Normalize broken PDF extraction across Russian, German, French, English, etc.

        Fixes:
        - Soft hyphen artifacts
        - Hyphenated line breaks
        - Artificial line wraps
        - Word fragmentation like: несмо тря, ничтожеств о
        - Excess whitespace
        """

        if not text:
            return ""

        import re

        # Normalize newlines
        text = text.replace("\r\n", "\n")

        # Remove soft hyphen (very common in Russian/German PDFs)
        text = text.replace("\u00ad", "")

        # Fix hyphenated line breaks
        # Schiff-\nfahrt → Schifffahrt
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

        # Fix broken words split by newline
        # судоро\nжно → судорожно
        text = re.sub(r"(\w)\n(\w)", r"\1 \2", text)

        # Fix mid-word splits caused by layout spacing
        # Works across Cyrillic + Latin scripts
        text = re.sub(
            r"(?<=\w)\s+(?=\w)",
            lambda m: "" if len(m.group(0).strip()) == 0 else " ",
            text
        )

        lines = text.split("\n")
        rebuilt = []

        sentence_endings = (".", "!", "?", "…", "»", "”")
        dialogue_starters = (
            "—", "-", "«", "„", "“", "\"", "'", ","
        )

        for line in lines:
            stripped = line.strip()

            if not stripped:
                rebuilt.append("")
                continue

            if not rebuilt:
                rebuilt.append(stripped)
                continue

            prev = rebuilt[-1]

            # If previous line ends sentence → new paragraph
            if prev.endswith(sentence_endings):
                rebuilt.append(stripped)

            # Dialogue start
            elif stripped.startswith(dialogue_starters):
                rebuilt.append(stripped)

            # Merge artificial wrap
            else:
                rebuilt[-1] += " " + stripped

        text = "\n".join(rebuilt)

        # Clean excessive whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()
