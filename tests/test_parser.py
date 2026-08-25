from lxml import etree
import pytest
from src.parser.models import DOCX_NS, RunType, RunView

def _run(inner: str) -> etree._Element:
    """Builds a <w:r> fragment with the w: namespace declared."""
    return etree.fromstring(f'<w:r xmlns:w="{DOCX_NS["w"]}">{inner}</w:r>')

# ------ MODEL TESTS ------
def test_text_run_has_text_type_and_matching_characters():
    run = RunView(_run("<w:t>Hi there</w:t>"), 0)

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
    run = RunView(_run(tag_xml), 0)

    assert run.type is expected_type
    assert [c.char for c in run.characters] == expected_chars


def test_run_without_run_properties_defaults_formatting_to_false():
    run = RunView(_run("<w:t>plain</w:t>"), 0)

    assert run.bold is False
    assert run.italic is False
    assert run.underline is False
    assert run.small_caps is False


def test_run_properties_set_each_formatting_flag_independently():
    bold_run = RunView(_run("<w:rPr><w:b/></w:rPr><w:t>x</w:t>"), 0)
    italic_run = RunView(_run("<w:rPr><w:i/></w:rPr><w:t>x</w:t>"), 0)
    underline_run = RunView(_run("<w:rPr><w:u/></w:rPr><w:t>x</w:t>"), 0)
    small_caps_run = RunView(_run("<w:rPr><w:smallCaps/></w:rPr><w:t>x</w:t>"), 0)

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
    run = RunView(_run("<w:rPr><w:b/><w:i/></w:rPr><w:t>x</w:t>"), 0)

    assert run.bold is True
    assert run.italic is True
    assert run.underline is False
    assert run.small_caps is False


def test_missing_text_element_has_no_characters():
    run = RunView(_run(""), 0)

    assert run.characters == []


def test_empty_text_element_has_no_characters():
    run = RunView(_run("<w:t></w:t>"), 0)

    assert run.characters == []


def test_footnote_id_returns_id_attribute():
    run = RunView(_run('<w:footnoteReference w:id="42"/>'), 0)

    assert run.footnote_id == "42"


def test_footnote_id_is_empty_for_non_footnote_run():
    run = RunView(_run("<w:t>not a footnote</w:t>"), 0)

    assert run.footnote_id == ""
