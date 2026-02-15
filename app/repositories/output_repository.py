from pathlib import Path

class OutputRepository:
    def save(self, path: str, content: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(content, encoding="utf-8")
