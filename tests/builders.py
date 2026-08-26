from lxml import etree
from src.parser.models import DOCX_NS, RunView
from src.extractor.models import CitationClause, CitationSentence


def run_xml(inner: str = "") -> etree._Element:
    """Builds a <w:r> fragment with the w: namespace declared."""
    return etree.fromstring(f'<w:r xmlns:w="{DOCX_NS["w"]}">{inner}</w:r>')


def run_view(inner: str = "", reading_order: int = 0) -> RunView:
    """Builds a RunView from a <w:r> fragment body."""
    return RunView(run_xml(inner), reading_order)


def text_run_view(text: str, reading_order: int = 0) -> RunView:
    """Builds a plain text RunView containing the given literal text."""
    return run_view(f"<w:t>{text}</w:t>", reading_order)


def clause_from_text(text: str) -> CitationClause:
    """Builds a CitationClause backed by real Characters."""
    return CitationClause(characters=text_run_view(text).characters)


def sentence_from_text(text: str) -> CitationSentence:
    """Builds a one-clause CitationSentence backed by real Characters."""
    return CitationSentence(clauses=[clause_from_text(text)])
