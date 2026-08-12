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
        

@dataclass
class Block:
    """
    A series of RunView objects. Represents a block of text split on paragraph 
    or footnote.
    """
    runs: List[RunView]
    reading_order: int
    type: BlockType = field(default=BlockType.PARAGRAPH)



class Document:
    """
    Final output object of Parser.
    """
    blocks: List[Block]
