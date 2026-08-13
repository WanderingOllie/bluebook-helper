import re
from enum import Enum, auto
from typing import List, Tuple
from dataclasses import dataclass
from src.parser.models import Block, RunView

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
class TextRange:
    _source_block: Block

    _start_run: RunView
    _start_offset: int  # inclusive

    _end_run: RunView
    _end_offset: int  # exclusive

    def get_text(self) -> str:
        runs = self._source_block.runs_between(self._start_run, self._end_run)

        if len(runs) == 1:
            return runs[0].get_text()[self._start_offset:self._end_offset]

        first_text = runs[0].get_text()[self._start_offset:]
        middle_text = "".join(run.get_text() for run in runs[1:-1])
        last_text = runs[-1].get_text()[:self._end_offset]
        return first_text + middle_text + last_text

    def get_source_block(self) -> Block:
        return self._source_block

    def get_start_run(self) -> RunView:
        return self._start_run

    def get_start_offset(self) -> int:
        return self._start_offset


@dataclass
class CitationClause:
    """Represents a single citation authority."""
    _text_range: TextRange
    _source_type: SourceType
    _citation_form: CitationForm
    _details: dict

@dataclass
class CitationSentence:
    """
    Manages a series of CitationClauses representing a single citation 
    sentence.
    """
    _text_range: TextRange
    _clauses: List[CitationClause]
