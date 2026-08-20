from dataclasses import dataclass, field
from typing import List
from src.parser.models import Block, BasicDocument, RunView

# TODO: Make Character and CharList work with iteration

@dataclass(eq=False)
class Character:
    """Manages a single character in a RunView."""
    _source_run: RunView
    _index: int  # index of char in RunView's text

    def get_char(self) -> str:
        text = self._source_run.get_text()
        return text[self._index]


@dataclass(eq=False)
class CharList:
    """List of all text Characters in a Block."""
    _source_block: Block
    _characters: List[Character] = field(default_factory=list)

    def add_char(self, char: Character):
        self._characters.append(char)

    def get_chars(self) -> List[Character]:
        return self._characters

    def get_source_block(self) -> Block:
        return self._source_block


class RefinedDocument:
    """Final output object of Refiner."""
    _blocks: List[Block]
    _char_map: dict[Block, CharList]

    def __init__(self, basic_doc: BasicDocument) -> None:
        self._blocks = basic_doc.get_blocks()
        self._char_map = {}
        
    def add_char_list(self, char_list: CharList) -> None:
        self._char_map[char_list.get_source_block()] = char_list

    def get_blocks(self) -> List[Block]:
        return self._blocks
