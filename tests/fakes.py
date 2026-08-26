class FakeLLM:
    """Stands in for LLM in tests."""

    def __init__(
        self,
        sentences: list[str] | None = None,
        clauses: dict[str, list[str]] | None = None,
    ) -> None:
        self._sentences = sentences if sentences is not None else []
        self._clauses = clauses if clauses is not None else {}

    def extract_citation_sentences(self, text: str) -> list[str]:
        return self._sentences

    def extract_citation_clauses(self, text: str) -> list[str]:
        """Defaults to one clause spanning the whole sentence."""
        return self._clauses.get(text, [text])
