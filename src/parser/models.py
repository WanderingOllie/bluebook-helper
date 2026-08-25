from __future__ import annotations
from enum import auto, Enum
from dataclasses import dataclass, field
from typing import List
from lxml import etree

# ----- CONSTANTS -----
DOCX_NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
}

class RunType(Enum):
    # Ordinary run
    TEXT = auto()

    # Whitespace / character elements
    TAB_CHAR = auto()
    LINE_BREAK = auto()
    CARRIAGE_RETURN = auto()
    NON_BREAKING_HYPHEN = auto()
    OPTIONAL_HYPHEN = auto()

    # Reference markers
    FOOTNOTE_REF = auto()
    ENDNOTE_REF = auto()
    COMMENT_REF = auto()

class BlockType(Enum):
    PARAGRAPH = auto()
    FOOTNOTE = auto()

_RUN_TYPE_MAP = {
    "w:tab": RunType.TAB_CHAR,
    "w:br": RunType.LINE_BREAK,
    "w:cr": RunType.CARRIAGE_RETURN,
    "w:noBreakHyphen": RunType.NON_BREAKING_HYPHEN,
    "w:softHyphen": RunType.OPTIONAL_HYPHEN,
    "w:footnoteReference": RunType.FOOTNOTE_REF,
    "w:endnoteReference": RunType.ENDNOTE_REF,
    "w:commentReference": RunType.COMMENT_REF,
}

# Non-TEXT RunTypes that still resolve to a citation-relevant character
# Anything mapped to None never produces a Character
_RUN_TYPE_CHARS = {
    # Word/line boundaries resolve to a space to separate adjacent text
    RunType.TAB_CHAR: " ",
    RunType.LINE_BREAK: " ",
    RunType.CARRIAGE_RETURN: " ",

    # Non-breaking hyphen is real content and resolves to a literal "-"
    RunType.NON_BREAKING_HYPHEN: "-",

    RunType.OPTIONAL_HYPHEN: None,
    RunType.FOOTNOTE_REF: None,
    RunType.ENDNOTE_REF: None,
    RunType.COMMENT_REF: None,
}

# ----- MAIN CLASSES -----
@dataclass(eq=False)
class RunView:
    """Manages a run XML object."""
    _run: etree._Element
    reading_order: int
    type: RunType = field(init=False, default=RunType.TEXT)
    bold: bool = field(init=False, default=False)
    italic: bool = field(init=False, default=False)
    underline: bool = field(init=False, default=False)
    small_caps: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        """Categorize the run's type and formatting from its child elements."""
        for tag, run_type in _RUN_TYPE_MAP.items():
            if self._run.find(tag, DOCX_NS) is not None:
                self.type = run_type
                break

        run_properties = self._run.find("w:rPr", DOCX_NS)
        if run_properties is not None:
            self.bold = run_properties.find("w:b", DOCX_NS) is not None
            self.italic = run_properties.find("w:i", DOCX_NS) is not None
            self.underline = run_properties.find("w:u", DOCX_NS) is not None
            self.small_caps = run_properties.find("w:smallCaps", DOCX_NS) is not None

    @property
    def footnote_id(self) -> str:
        """Returns the run's footnote id if it's a footnote reference."""
        footnote_ref = self._run.find("w:footnoteReference", DOCX_NS)
        if footnote_ref is None:
            return ""
        return footnote_ref.get(f"{{{DOCX_NS['w']}}}id") or ""

    @property
    def characters(self) -> List[Character]:
        """Returns citation-relevant Characters per _RUN_TYPE_CHARS."""
        if self.type == RunType.TEXT:
            text_element = self._run.find("w:t", DOCX_NS)
            t = (text_element.text or "") if text_element is not None else ""
            return [
                Character(self, i, ch) for i, ch in enumerate(t)
            ]

        char = _RUN_TYPE_CHARS.get(self.type)
        return [Character(self, 0, char)] if char is not None else []


@dataclass(eq=False)
class Character:
    """A single citation-relevant character."""
    _source_run: RunView
    _index: int  # position of this character within _source_run
    char: str

    @property
    def bold(self) -> bool:
        return self._source_run.bold

    @property
    def italic(self) -> bool:
        return self._source_run.italic

    @property
    def underline(self) -> bool:
        return self._source_run.underline

    @property
    def small_caps(self) -> bool:
        return self._source_run.small_caps

    @property
    def run_type(self) -> RunType:
        return self._source_run.type


@dataclass(eq=False)
class Block:
    """
    A series of RunView objects. Represents a block of text split on paragraph
    or footnote.
    """
    reading_order: int
    type: BlockType = field(default=BlockType.PARAGRAPH)
    runs: List[RunView] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "".join(char.char for run in self.runs for char in run.characters)


@dataclass(eq=False)
class BasicDocument:
    """
    Final output object of Parser.
    """
    blocks: List[Block] = field(default_factory=list)
