from typing import Tuple
import re
from src.parser.models import Block
from src.extractor.models import TextRange


def locate(text: str, needle: str, start: int = 0) -> Tuple[int, int]:
    """
    Finds needle within text starting at index start. Returns the
    (start, end) character offsets of the match, with end exclusive.
    """
    index = text.find(needle, start)
    if index != -1:
        return index, index + len(needle)

    # Fallback to try whitespace-tolerant match 
    pattern = re.compile(r"\s+".join(re.escape(word) for word in needle.split()))
    match = pattern.search(text, start)
    if match is None:
        raise ValueError(f"Could not locate {needle!r} in text starting at index {start}.")

    return match.start(), match.end()

def locate_range(block: Block, needle: str, start: int = 0) -> TextRange:
    """Locates needle within block's own text and builds a TextRange."""
    span_start, span_end = locate(block.get_text(), needle, start)
    start_run, start_offset, end_run, end_offset = block.resolve_span(span_start, span_end)
    return TextRange(block, start_run, start_offset, end_run, end_offset)

def locate_nested_range(parent: TextRange, needle: str, start: int = 0) -> TextRange:
    """Locates needle within parent's own text and builds a nested TextRange."""
    block = parent.get_source_block()
    local_start, local_end = locate(parent.get_text(), needle, start)

    block_base = block.flat_offset_of(parent.get_start_run(), parent.get_start_offset())
    start_run, start_offset, end_run, end_offset = block.resolve_span(
        block_base + local_start, block_base + local_end
    )
    return TextRange(block, start_run, start_offset, end_run, end_offset)
