from lxml import etree
from src.parser.models import BasicDocument, Block, BlockType, DOCX_NS, RunView
from src.parser.parser import Parser
from src.refiner.models import RefinedDocument
from src.refiner.refiner import Refiner
from helpers import build_tier_docx, TestFileTier


def _run_view(inner: str, reading_order: int = 0) -> RunView:
    """Builds a RunView from a <w:r> fragment with the w: namespace declared."""
    xml = etree.fromstring(f'<w:r xmlns:w="{DOCX_NS["w"]}">{inner}</w:r>')
    return RunView(xml, reading_order)


def test_refined_document_copies_blocks_and_starts_with_empty_char_map():
    block = Block(0, BlockType.PARAGRAPH, [_run_view("<w:t>hi</w:t>")])
    basic_doc = BasicDocument(blocks=[block])

    refined_doc = RefinedDocument(basic_doc)

    assert refined_doc.blocks is basic_doc.blocks
    assert refined_doc.char_map == {}


def test_refine_populates_one_char_map_entry_per_block():
    block_a = Block(0, BlockType.PARAGRAPH, [_run_view("<w:t>a</w:t>")])
    block_b = Block(1, BlockType.FOOTNOTE, [_run_view("<w:t>b</w:t>")])
    basic_doc = BasicDocument(blocks=[block_a, block_b])

    refined_doc = Refiner(basic_doc).refine()

    assert set(refined_doc.char_map.keys()) == {block_a, block_b}


def test_single_run_block_char_map_matches_run_characters():
    block = Block(0, BlockType.PARAGRAPH, [_run_view("<w:t>hi</w:t>")])
    basic_doc = BasicDocument(blocks=[block])

    refined_doc = Refiner(basic_doc).refine()

    assert [c.char for c in refined_doc.char_map[block]] == ["h", "i"]


def test_multi_run_block_flattens_in_run_order():
    block = Block(
        0,
        BlockType.PARAGRAPH,
        [_run_view("<w:t>Hello</w:t>"), _run_view("<w:t> world</w:t>")],
    )
    basic_doc = BasicDocument(blocks=[block])

    refined_doc = Refiner(basic_doc).refine()

    chars = "".join(c.char for c in refined_doc.char_map[block])
    assert chars == block.text == "Hello world"


def test_zero_run_block_has_empty_char_map_entry():
    block = Block(0, BlockType.PARAGRAPH, [])
    basic_doc = BasicDocument(blocks=[block])

    refined_doc = Refiner(basic_doc).refine()

    assert refined_doc.char_map[block] == []


def test_mixed_run_types_flatten_in_order_within_a_block():
    block = Block(
        0,
        BlockType.PARAGRAPH,
        [
            _run_view("<w:t>A</w:t>"),
            _run_view("<w:tab/>"),
            _run_view('<w:footnoteReference w:id="1"/>'),
            _run_view("<w:t>B</w:t>"),
        ],
    )
    basic_doc = BasicDocument(blocks=[block])

    refined_doc = Refiner(basic_doc).refine()

    assert [c.char for c in refined_doc.char_map[block]] == ["A", " ", "B"]


def test_multiple_blocks_have_isolated_char_map_entries():
    block_a = Block(0, BlockType.PARAGRAPH, [_run_view("<w:t>para</w:t>")])
    block_b = Block(1, BlockType.FOOTNOTE, [_run_view("<w:t>note</w:t>")])
    basic_doc = BasicDocument(blocks=[block_a, block_b])

    refined_doc = Refiner(basic_doc).refine()

    assert [c.char for c in refined_doc.char_map[block_a]] == list("para")
    assert [c.char for c in refined_doc.char_map[block_b]] == list("note")


def test_characters_retain_formatting_through_refiner():
    run = _run_view("<w:rPr><w:b/><w:i/></w:rPr><w:t>x</w:t>")
    block = Block(0, BlockType.PARAGRAPH, [run])
    basic_doc = BasicDocument(blocks=[block])

    refined_doc = Refiner(basic_doc).refine()
    char = refined_doc.char_map[block][0]

    assert char.bold is True
    assert char.italic is True
    assert char.underline is False
    assert char.small_caps is False


def test_refine_after_parsing_split_on_footnote_fixture(tmp_path):
    """Integration: Parser output flows into Refiner without losing content."""
    path = build_tier_docx(tmp_path, TestFileTier.UTIL, name="split_on_footnote")
    basic_doc = Parser(str(path)).parse()

    refined_doc = Refiner(basic_doc).refine()

    assert refined_doc.blocks is basic_doc.blocks
    assert [b.type for b in refined_doc.blocks] == [
        BlockType.PARAGRAPH,
        BlockType.FOOTNOTE,
        BlockType.PARAGRAPH,
    ]
    for block in refined_doc.blocks:
        assert "".join(c.char for c in refined_doc.char_map[block]) == block.text
