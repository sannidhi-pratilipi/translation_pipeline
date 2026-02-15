import re

class ChunkingService:
    """
    Chunk long documents into semantically coherent segments.

    Strategy:
    - First, respect paragraph boundaries (split on blank lines).
    - Within very long paragraphs, fall back to sentence boundaries.
    - Never cut in the middle of a sentence if it can be avoided.
    """
    def _reconstruct_paragraphs(self, text: str) -> list[str]:
        """
        Reconstruct paragraphs from messy PDF text.
        Works for Russian, German, French.
        """

        lines = text.split("\n")
        paragraphs = []
        current = ""

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current:
                    paragraphs.append(current.strip())
                    current = ""
                continue

            # Dialogue line (Russian style)
            if stripped.startswith(("—", "«", "„", "\"")):
                if current:
                    paragraphs.append(current.strip())
                paragraphs.append(stripped)
                current = ""
                continue

            # If previous ends with full stop and new line starts uppercase
            if (
                current
                and current.endswith((".", "!", "?", "…", "»"))
                and stripped[0].isupper()
            ):
                paragraphs.append(current.strip())
                current = stripped
            else:
                current += " " + stripped if current else stripped

        if current:
            paragraphs.append(current.strip())

        return paragraphs

    _sentence_pattern = re.compile( r"(?<=[.!?…»”])\s+(?=[A-ZА-ЯЁ])")

    def _split_into_sentences(self, paragraph: str) -> list[str]:
        paragraph = paragraph.strip()
        if not paragraph:
            return []

        # Protect common abbreviations (basic multilingual safety)
        abbreviations = [
            "r.", "ул.", "т.д.", "т.п.",  # Russian
            "Mr.", "Mrs.", "Dr.", "Prof.",  # English/German
            "z.B.", "usw.",  # German
            "M.", "Mme.", "Dr."  # French
        ]

        placeholder = "§§§"

        for abbr in abbreviations:
            paragraph = paragraph.replace(abbr, abbr.replace(".", placeholder))

        sentences = self._sentence_pattern.split(paragraph)

        # Restore periods
        sentences = [
            s.replace(placeholder, ".").strip()
            for s in sentences if s.strip()
        ]

        return sentences

    def chunk(self, text: str, max_chars: int = 2500) -> list[str]:
        """
        Split `text` into segments of at most `max_chars` characters, trying to:
        - keep whole paragraphs together where possible
        - otherwise, break on sentence boundaries
        This helps the model preserve local context and semantics.
        """
        if not text or not text.strip():
            return []

        paragraphs = self._reconstruct_paragraphs(text)

        chunks: list[str] = []
        current: str = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If the entire paragraph fits, keep it as a whole.
            if len(current) + len(para) + 2 <= max_chars:
                current = (current + "\n\n" + para).strip() if current else para
                continue

            # If the paragraph alone is too long, split it into sentences.
            sentences = self._split_into_sentences(para)
            for sent in sentences:
                # +1 for a space or newline separator
                projected_len = len(current) + len(sent) + (1 if current else 0)
                if projected_len <= max_chars:
                    current = f"{current} {sent}".strip() if current else sent
                else:
                    if current:
                        chunks.append(current.strip())
                    current = sent

            if current and not current.endswith("\n\n"):
                current = current + "\n\n"

        if current and current.strip():
            chunks.append(current.strip())

        return chunks
