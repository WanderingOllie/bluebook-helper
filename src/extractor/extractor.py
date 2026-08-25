from typing import Optional
import re
from src.parser.models import Block
from src.refiner.models import RefinedDocument
from src.extractor.models import CitationClause, CitationSentence, ExtractedDocument
from src.llm.client import LLM


_CITATION_SIGNAL_PATTERNS = [
    re.compile(r"§"),                                    # section symbol
    re.compile(r"\bv\.\s"),                              # case name separator
    re.compile(r"\(\d{4}\)"),                            # citation year, e.g. "(1954)"
    re.compile(r"\b\d+\s+[A-Z][A-Za-z.]{1,10}\s+\d+\b"), # reporter cite, e.g. "347 U.S. 483"
    re.compile(r"\bid\.", re.IGNORECASE),                # short-form citation
    re.compile(r"\bsupra\b|\binfra\b", re.IGNORECASE),
    re.compile(r"\bU\.S\.C\.|\bC\.F\.R\."),
]

class Extractor:
    """Takes in a RefinedDocument and produces an ExtractedDocument."""

    def __init__(self, document: RefinedDocument, llm: Optional[LLM] = None) -> None:
        self._document = document
        self._llm = llm if llm is not None else LLM()

    def extract(self) -> ExtractedDocument:
        extracted_doc = ExtractedDocument(self._document)

        for block in self._document.blocks:
            if not self._filter_block(block):
                continue
            extracted_doc.sentences.extend(self._extract_sentences(block))

        return extracted_doc

    def _extract_sentences(self, block: Block) -> list[CitationSentence]:
        """Extracts every CitationSentence found in a single block."""
        block_text = block.text
        block_chars = self._document.char_map[block]
        sentences = []

        for sentence_text in self._llm.extract_citation_sentences(block_text):
            sentence_start = block_text.index(sentence_text)
            clauses = []

            for clause_text in self._llm.extract_citation_clauses(sentence_text):
                clause_start = sentence_start + sentence_text.index(clause_text)
                clause_end = clause_start + len(clause_text)
                characters = block_chars[clause_start:clause_end]
                clauses.append(CitationClause(characters=characters))

            sentences.append(CitationSentence(clauses=clauses))

        return sentences

    @staticmethod
    def _filter_block(block: Block) -> bool:
        """Checks if a Block is likely to have citations inside."""
        return any(pattern.search(block.text) for pattern in _CITATION_SIGNAL_PATTERNS)
