from typing import List
from src.parser.models import Block, BasicDocument, Character


class RefinedDocument:
    """Final output object of Refiner."""

    def __init__(self, basic_doc: BasicDocument) -> None:
        self.blocks: List[Block] = basic_doc.blocks
        self.char_map: dict[Block, List[Character]] = {}
