import pytest
from src.parser.models import BlockType, DOCX_NS, RunType
from src.parser.parser import Parser
from builders import run_view
from helpers import build_docx, build_tier_docx, TestFileTier

def _r(inner: str = "") -> str:
    """<w:r> fragment string, for embedding in a larger document/footnotes body."""
    return f"<w:r>{inner}</w:r>"


def _document(body_xml: str) -> str:
    """Wraps body content in a minimal <w:document> for Parser."""
    return f'<w:document xmlns:w="{DOCX_NS["w"]}"><w:body>{body_xml}</w:body></w:document>'


def _footnotes(*footnotes_xml: str) -> str:
    """Wraps footnote entries in a minimal <w:footnotes> for Parser."""
    return f'<w:footnotes xmlns:w="{DOCX_NS["w"]}">{"".join(footnotes_xml)}</w:footnotes>'


def _footnote(footnote_id: str, inner: str) -> str:
    return f'<w:footnote w:id="{footnote_id}">{inner}</w:footnote>'

# ------ MODEL TESTS ------
def test_text_run_has_text_type_and_matching_characters():
    run = run_view("<w:t>Hi there</w:t>")

    assert run.type is RunType.TEXT
    assert [c.char for c in run.characters] == list("Hi there")


@pytest.mark.parametrize(
    "tag_xml,expected_type,expected_chars",
    [
        ("<w:tab/>", RunType.TAB_CHAR, [" "]),
        ("<w:br/>", RunType.LINE_BREAK, [" "]),
        ("<w:cr/>", RunType.CARRIAGE_RETURN, [" "]),
        ("<w:noBreakHyphen/>", RunType.NON_BREAKING_HYPHEN, ["-"]),
        ("<w:softHyphen/>", RunType.OPTIONAL_HYPHEN, []),
        ('<w:footnoteReference w:id="1"/>', RunType.FOOTNOTE_REF, []),
        ('<w:endnoteReference w:id="1"/>', RunType.ENDNOTE_REF, []),
        ('<w:commentReference w:id="1"/>', RunType.COMMENT_REF, []),
    ],
)
def test_special_tags_map_to_run_type_and_characters(
    tag_xml, expected_type, expected_chars
):
    run = run_view(tag_xml)

    assert run.type is expected_type
    assert [c.char for c in run.characters] == expected_chars


def test_run_without_run_properties_defaults_formatting_to_false():
    run = run_view("<w:t>plain</w:t>")

    assert run.bold is False
    assert run.italic is False
    assert run.underline is False
    assert run.small_caps is False


def test_run_properties_set_each_formatting_flag_independently():
    bold_run = run_view("<w:rPr><w:b/></w:rPr><w:t>x</w:t>")
    italic_run = run_view("<w:rPr><w:i/></w:rPr><w:t>x</w:t>")
    underline_run = run_view("<w:rPr><w:u/></w:rPr><w:t>x</w:t>")
    small_caps_run = run_view("<w:rPr><w:smallCaps/></w:rPr><w:t>x</w:t>")

    assert (bold_run.bold, bold_run.italic, bold_run.underline, bold_run.small_caps) == (
        True, False, False, False,
    )
    assert (italic_run.bold, italic_run.italic, italic_run.underline, italic_run.small_caps) == (
        False, True, False, False,
    )
    assert (underline_run.bold, underline_run.italic, underline_run.underline, underline_run.small_caps) == (
        False, False, True, False,
    )
    assert (small_caps_run.bold, small_caps_run.italic, small_caps_run.underline, small_caps_run.small_caps) == (
        False, False, False, True,
    )


def test_run_properties_combine_multiple_formatting_flags():
    run = run_view("<w:rPr><w:b/><w:i/></w:rPr><w:t>x</w:t>")

    assert run.bold is True
    assert run.italic is True
    assert run.underline is False
    assert run.small_caps is False


def test_missing_text_element_has_no_characters():
    run = run_view("")

    assert run.characters == []


def test_empty_text_element_has_no_characters():
    run = run_view("<w:t></w:t>")

    assert run.characters == []


def test_footnote_id_returns_id_attribute():
    run = run_view('<w:footnoteReference w:id="42"/>')

    assert run.footnote_id == "42"


def test_footnote_id_is_empty_for_non_footnote_run():
    run = run_view("<w:t>not a footnote</w:t>")

    assert run.footnote_id == ""

# ------ PARSER TESTS ------
def test_single_paragraph_without_footnotes_produces_one_block(tmp_path):
    document_xml = _document(f"<w:p>{_r('<w:t>Hello world</w:t>')}</w:p>")
    path = build_docx(tmp_path, document_xml)

    document = Parser(str(path)).parse()

    assert len(document.blocks) == 1
    assert document.blocks[0].type is BlockType.PARAGRAPH
    assert document.blocks[0].text == "Hello world"


def test_footnote_reference_splits_paragraph_into_three_blocks(tmp_path):
    path = build_tier_docx(tmp_path, TestFileTier.UTIL, name="split_on_footnote")

    document = Parser(str(path)).parse()

    assert [(b.type, b.text) for b in document.blocks] == [
        (
            BlockType.PARAGRAPH,
            "Returning to our hypothetical foreign minister of a U.S. trading "
            "partner, if that foreign minister were to choose to petition or "
            "lobby the agency that makes distilled-spirits regulations, that "
            "agency would be the Department of the Treasury’s Alcohol and "
            "Tobacco Tax and Trade Bureau (TTB), which regulates spirits.",
        ),
        (
            BlockType.FOOTNOTE,
            " See 27 U.S.C. § 205(e) (2024) (explaining that the Secretary "
            "of the Treasury Department is in control of regulating the "
            "labeling of spirits).",
        ),
        (
            BlockType.PARAGRAPH,
            " TTB monitors and oversees the definitions, labeling, and "
            "movement through interstate and foreign commerce of wines and "
            "spirits.",
        ),
    ]


def test_unmatched_footnote_reference_id_is_skipped(tmp_path):
    """Guards the parser.py:60 fallback for a footnote ref with no matching id."""
    path = build_tier_docx(tmp_path, TestFileTier.UTIL, name="no_matching_footnote")

    document = Parser(str(path)).parse()

    assert [b.type for b in document.blocks] == [
        BlockType.PARAGRAPH,
        BlockType.PARAGRAPH,
    ]
    assert document.blocks[0].text.startswith("Returning to our hypothetical")
    assert document.blocks[1].text.startswith(" TTB monitors")


def test_missing_footnotes_part_skips_footnote_reference(tmp_path):
    path = build_tier_docx(tmp_path, TestFileTier.UTIL, name="missing_footnotes")

    document = Parser(str(path)).parse()

    assert [b.type for b in document.blocks] == [
        BlockType.PARAGRAPH,
        BlockType.PARAGRAPH,
    ]
    assert document.blocks[0].text.startswith("Returning to our hypothetical")
    assert document.blocks[1].text.startswith(" TTB monitors")


def test_two_footnote_references_in_one_paragraph_split_into_five_blocks(tmp_path):
    body = (
        "<w:p>"
        + _r("<w:t>A</w:t>")
        + _r('<w:footnoteReference w:id="1"/>')
        + _r("<w:t>B</w:t>")
        + _r('<w:footnoteReference w:id="2"/>')
        + _r("<w:t>C</w:t>")
        + "</w:p>"
    )
    document_xml = _document(body)
    footnotes_xml = _footnotes(
        _footnote("1", _r("<w:t>one</w:t>")),
        _footnote("2", _r("<w:t>two</w:t>")),
    )
    path = build_docx(tmp_path, document_xml, footnotes_xml)

    document = Parser(str(path)).parse()

    assert [(b.type, b.text) for b in document.blocks] == [
        (BlockType.PARAGRAPH, "A"),
        (BlockType.FOOTNOTE, "one"),
        (BlockType.PARAGRAPH, "B"),
        (BlockType.FOOTNOTE, "two"),
        (BlockType.PARAGRAPH, "C"),
    ]


def test_reading_order_is_monotonic_across_blocks_and_runs(tmp_path):
    path = build_tier_docx(tmp_path, TestFileTier.UTIL, name="split_on_footnote")

    document = Parser(str(path)).parse()

    block_orders = [b.reading_order for b in document.blocks]
    assert block_orders == list(range(len(block_orders)))

    run_orders = [r.reading_order for b in document.blocks for r in b.runs]
    assert run_orders == sorted(run_orders)
    assert len(set(run_orders)) == len(run_orders)


def test_paragraph_with_no_runs_produces_no_blocks(tmp_path):
    document_xml = _document("<w:p/>")
    path = build_docx(tmp_path, document_xml)

    document = Parser(str(path)).parse()

    assert document.blocks == []
