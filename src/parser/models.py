from dataclasses import dataclass, field
from typing import List
from lxml import etree
from src.constants import BlockType, DOCX_NS, RUN_TYPE_MAP, RunType


@dataclass
class RunView:
    """Manages a run XML object."""
    run: etree.Element
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
        return text_element.text if text_element is not None else ""

    def get_footnote_id(self) -> str:
        """Returns the run's footnote id if it's a footnote reference."""
        footnote_ref = self.run.find("w:footnoteReference", DOCX_NS)
        footnote_id = footnote_ref.get(f"{{{DOCX_NS['w']}}}id")
        return footnote_id

    def is_footnote_ref(self) -> bool:
            """Returns if the run is a footnote reference."""
            return self.type == RunType.FOOTNOTE_REF


@dataclass
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

    def get_runs(self) -> List[RunView]:
        return self._runs


@dataclass
class Document:
    """
    Final output object of Parser.
    """
    _blocks: List[Block] = field(default_factory=list)

    def add_block(self, block: Block) -> None:
        self._blocks.append(block)

    def get_blocks(self) -> List[Block]:
        return self._blocks
