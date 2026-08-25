from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List, Optional
from src.parser.models import Block, Character
from src.extractor.models import CitationSentence, ExtractedDocument, CitationClause


class RuleRunsOn(Enum):
    """Enum for whether Rules run against sentences or clauses."""
    SENTENCE = auto()
    CLAUSE = auto()


@dataclass
class Issue:
    """A single problem spotted by a Rule, anchored to source Characters."""
    location: CitationSentence | CitationClause
    starting_char: Character
    ending_char: Optional[Character]
    comment: str


@dataclass
class Rule:
    name: str
    runs_on: RuleRunsOn
    check: Callable[[CitationSentence | CitationClause], List[Issue]]

    def run(self, target: CitationSentence | CitationClause) -> List[Issue]:
        return self.check(target)


class SpottedDoc:
    """Final output of Spotter."""

    def __init__(self, extracted_doc: ExtractedDocument) -> None:
        self.blocks: List[Block] = extracted_doc.blocks
        self.sentences: List[CitationSentence] = extracted_doc.sentences
        self.issues: List[Issue] = []
