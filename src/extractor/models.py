from enum import Enum, auto
from typing import List, Optional
from dataclasses import dataclass, field
from src.parser.models import Block, Character
from src.refiner.models import RefinedDocument

# ----- CONSTANTS -----
class SourceType(Enum):
    """What kind of authority is being cited. Orthogonal to CitationForm."""
    CASE = auto()
    STATUTE = auto()
    BOOK = auto()
    REPORT = auto()
    PERIODICAL = auto()
    CONSTITUTION = auto()
    LEGISLATIVE_MATERIALS = auto()
    ADMINISTRATIVE_EXEC_MATERIALS = auto()
    UNPUBLISHED = auto()  # or forthcoming
    INTERNET = auto()
    ELECTRONIC_MEDIA = auto()
    FOREIGN_MATERIALS = auto()
    INTERNATIONAL_MATERIALS = auto()
    TRIBAL_NATIONS = auto()
    ARCHIVAL = auto()
    OTHER = auto()

class CitationForm(Enum):
    """How the citation refers to its source."""
    FULL = auto()
    SHORT_FORM = auto()
    ID = auto()
    SUPRA = auto()
    INFRA = auto()

# ----- MAIN CLASSES -----
@dataclass
class CitationClause:
    """Represents a single citation authority."""
    characters: List[Character] = field(default_factory=list)
    source_type: Optional[SourceType] = None
    citation_form: Optional[CitationForm] = None
    details: dict = field(default_factory=dict)

    @property
    def text(self) -> str:
        return "".join(char.char for char in self.characters)


@dataclass
class CitationSentence:
    """
    Manages a series of CitationClauses representing a single citation
    sentence.
    """
    clauses: List[CitationClause]

    @property
    def text(self) -> str:
        return "".join(clause.text for clause in self.clauses)

    @property
    def characters(self) -> List[Character]:
        return [char for clause in self.clauses for char in clause.characters]


class ExtractedDocument:
    """Final output object of Extractor."""

    def __init__(self, refined_doc: RefinedDocument) -> None:
        self.blocks: List[Block] = refined_doc.blocks
        self.sentences: List[CitationSentence] = []
