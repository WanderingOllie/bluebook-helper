from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Tuple
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

RUN_TYPE_MAP = {
    "w:tab": RunType.TAB_CHAR,
    "w:br": RunType.LINE_BREAK,
    "w:cr": RunType.CARRIAGE_RETURN,
    "w:noBreakHyphen": RunType.NON_BREAKING_HYPHEN,
    "w:softHyphen": RunType.OPTIONAL_HYPHEN,
    "w:footnoteReference": RunType.FOOTNOTE_REF,
    "w:endnoteReference": RunType.ENDNOTE_REF,
    "w:commentReference": RunType.COMMENT_REF,
}

class BlockType(Enum):
    PARAGRAPH = auto()
    FOOTNOTE = auto()

# ----- MAIN CLASSES -----
@dataclass(eq=False)
class RunView:
    """Manages a run XML object."""
    run: etree._Element
    reading_order: int
    type: RunType = field(init=False, default=RunType.TEXT)

    def __post_init__(self) -> None:
        """Categorize the run's type based on its child elements."""
        for tag, run_type in RUN_TYPE_MAP.items():
            if self.run.find(tag, DOCX_NS) is not None:
                self.type = run_type
                break

    def get_text(self) -> str:
        """Returns text of run or a blank string."""
        text_element = self.run.find("w:t", DOCX_NS)
        if text_element is None:
            return ""
        return text_element.text or ""

    def get_footnote_id(self) -> str:
        """Returns the run's footnote id if it's a footnote reference."""
        footnote_ref = self.run.find("w:footnoteReference", DOCX_NS)
        if footnote_ref is None:
            return ""
        return footnote_ref.get(f"{{{DOCX_NS['w']}}}id") or ""

    def is_footnote_ref(self) -> bool:
            """Returns if the run is a footnote reference."""
            return self.type == RunType.FOOTNOTE_REF


@dataclass(eq=False)
class Block:
    """
    A series of RunView objects. Represents a block of text split on paragraph
    or footnote.
    """
    reading_order: int
    type: BlockType = field(default=BlockType.PARAGRAPH)
    _runs: List[RunView] = field(default_factory=list)

    def add_run(self, run: RunView) -> None:
        self._runs.append(run)

    def get_text(self) -> str:
        """Returns flat string of all text in Block's runs."""
        text = "".join(run.get_text() for run in self.get_runs())
        return text

    def get_runs(self) -> List[RunView]:
        return self._runs

    # def runs_between(self, start_run: RunView, end_run: RunView
    # ) -> List[RunView]:
    #     """Returns the runs from start_run to end_run, inclusive."""
    #     start_index = self._runs.index(start_run)
    #     end_index = self._runs.index(end_run)
    #     return self._runs[start_index:end_index + 1]

    # def resolve_offset(self, offset: int) -> Tuple[RunView, int]:
    #     """
    #     Given a character offset into block.get_text(), return which run
    #     owns that character and the offset within that run's text.
    #     """
    #     runs = self.get_runs()
    #     char_count = 0

    #     for run in runs:
    #         pre_count = char_count
    #         char_count += len(run.get_text())
    #         if pre_count <= offset < char_count:
    #             return run, offset - pre_count

    #     raise ValueError(
    #         f"Offset {offset} is out of bounds for block text of length {char_count}."
    #     )

    # def flat_offset_of(self, run: RunView, local_offset: int) -> int:
    #         """
    #         Given a run belonging to this block and an offset within that
    #         run's own text, return the corresponding flat offset into
    #         block.get_text(). The inverse of resolve_offset.
    #         """
    #         char_count = 0
    #         for candidate in self.get_runs():
    #             if candidate is run:
    #                 return char_count + local_offset
    #             char_count += len(candidate.get_text())
    
    #         raise ValueError(f"{run!r} does not belong to this block.")

    # def resolve_span(
    #     self, start: int, end: int
    # ) -> Tuple[RunView, int, RunView, int]:
    #     """
    #     Given a flat [start, end) character span into block.get_text(),
    #     return (start_run, start_offset, end_run, end_offset) ready to
    #     build a TextRange.
    #     """
    #     start_run, start_offset = self.resolve_offset(start)
    #     end_run, end_offset = self.resolve_offset(end - 1)
    #     return start_run, start_offset, end_run, end_offset + 1


@dataclass(eq=False)
class BasicDocument:
    """
    Final output object of Parser.
    """
    _blocks: List[Block] = field(default_factory=list)

    def add_block(self, block: Block) -> None:
        self._blocks.append(block)

    def get_blocks(self) -> List[Block]:
        return self._blocks
