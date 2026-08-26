from src.parser.models import BasicDocument, Block, BlockType
from src.parser.parser import Parser
from src.refiner.models import RefinedDocument
from src.refiner.refiner import Refiner
from src.extractor.extractor import Extractor
from builders import run_view
from fakes import FakeLLM
from helpers import build_docx


def _refined_block(text: str) -> tuple[RefinedDocument, Block]:
    """Builds a one-run, one-block RefinedDocument containing text."""
    block = Block(0, BlockType.PARAGRAPH, [run_view(f"<w:t>{text}</w:t>")])
    basic_doc = BasicDocument(blocks=[block])
    return Refiner(basic_doc).refine(), block


# ------ FILTER TESTS ------
def test_filter_block_matches_case_citation_signal():
    _, block = _refined_block("Smith v. Jones is a famous case.")

    assert Extractor._filter_block(block) is True


def test_filter_block_matches_reporter_citation_signal():
    _, block = _refined_block("See 347 U.S. 483 for details.")

    assert Extractor._filter_block(block) is True


def test_filter_block_rejects_block_without_citation_signal():
    _, block = _refined_block("Just plain prose, nothing citation-like here.")

    assert Extractor._filter_block(block) is False


# ------ EXTRACTOR TESTS ------
def test_extract_builds_one_sentence_from_one_block():
    text = "Prose. Smith v. Jones, 347 U.S. 483 (1954). More prose."
    refined_doc, _ = _refined_block(text)
    llm = FakeLLM(sentences=["Smith v. Jones, 347 U.S. 483 (1954)."])

    extracted_doc = Extractor(refined_doc, llm).extract()

    assert len(extracted_doc.sentences) == 1
    assert extracted_doc.sentences[0].text == "Smith v. Jones, 347 U.S. 483 (1954)."


def test_extract_splits_sentence_into_clauses():
    text = "See Smith v. Jones, 347 U.S. 483 (1954); Doe v. Roe, 410 U.S. 113 (1973)."
    refined_doc, _ = _refined_block(text)
    llm = FakeLLM(
        sentences=[text],
        clauses={
            text: [
                "Smith v. Jones, 347 U.S. 483 (1954)",
                "Doe v. Roe, 410 U.S. 113 (1973)",
            ]
        },
    )

    extracted_doc = Extractor(refined_doc, llm).extract()

    clauses = extracted_doc.sentences[0].clauses
    assert [c.text for c in clauses] == [
        "Smith v. Jones, 347 U.S. 483 (1954)",
        "Doe v. Roe, 410 U.S. 113 (1973)",
    ]


def test_extract_skips_blocks_without_citation_signal():
    refined_doc, _ = _refined_block("Just plain prose, nothing citation-like here.")
    llm = FakeLLM(sentences=["should never be requested"])

    extracted_doc = Extractor(refined_doc, llm).extract()

    assert extracted_doc.sentences == []


def test_extract_preserves_formatting_through_characters():
    block = Block(
        0,
        BlockType.PARAGRAPH,
        [
            run_view("<w:t>Foo </w:t>"),
            run_view("<w:rPr><w:i/></w:rPr><w:t>Id.</w:t>"),
            run_view("<w:t> bar.</w:t>"),
        ],
    )
    basic_doc = BasicDocument(blocks=[block])
    refined_doc = Refiner(basic_doc).refine()
    llm = FakeLLM(sentences=["Id."])

    extracted_doc = Extractor(refined_doc, llm).extract()

    characters = extracted_doc.sentences[0].characters
    assert "".join(c.char for c in characters) == "Id."
    assert all(c.italic for c in characters)


def test_extracted_document_propagates_blocks():
    refined_doc, _ = _refined_block("Smith v. Jones, 347 U.S. 483 (1954).")
    llm = FakeLLM(sentences=[])

    extracted_doc = Extractor(refined_doc, llm).extract()

    assert extracted_doc.blocks is refined_doc.blocks


def test_extract_after_real_parser_and_refiner(tmp_path):
    """Integration: a real Parser/Refiner document flows into Extractor."""
    document_xml = (
        f'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body><w:p><w:r><w:t>Smith v. Jones, 347 U.S. 483 (1954).</w:t></w:r></w:p></w:body>"
        f"</w:document>"
    )
    path = build_docx(tmp_path, document_xml)
    basic_doc = Parser(str(path)).parse()
    refined_doc = Refiner(basic_doc).refine()
    llm = FakeLLM(sentences=["Smith v. Jones, 347 U.S. 483 (1954)."])

    extracted_doc = Extractor(refined_doc, llm).extract()

    assert len(extracted_doc.sentences) == 1
    assert extracted_doc.sentences[0].text == "Smith v. Jones, 347 U.S. 483 (1954)."
