from enum import Enum, auto
from pathlib import Path
import zipfile

DOCUMENT_PART = "word/document.xml"
FOOTNOTES_PART = "word/footnotes.xml"

FILES_DIR = Path(__file__).parent / "files"

class TestFileTier(Enum):
    BASIC = auto()       # most basic case (prose, in-text cites, no footnotes)
    FOOTNOTE = auto()    # basic case plus foonotes
    COMPLEX = auto()     # footnote case plus comments and tracked changes

def build_docx(
    tmp_path: Path,
    document_xml: str,
    footnotes_xml: str | None = None,
    name: str = "test.docx",
) -> Path:
    """
    Zips document_xml (and footnotes_xml) into a .docx package for Parser.
    """
    docx_path = tmp_path / name
    with zipfile.ZipFile(docx_path, "w") as z:
        z.writestr(DOCUMENT_PART, document_xml)
        if footnotes_xml is not None:
            z.writestr(FOOTNOTES_PART, footnotes_xml)
    return docx_path


def read_fixture(tier: TestFileTier, part: str = "document") -> str | None:
    """
    Reads a fixture XML part for a tier.
    """
    path = FILES_DIR / tier.name.lower() / f"{part}.xml"
    return path.read_text(encoding="utf-8") if path.exists() else None


def build_tier_docx(
    tmp_path: Path, 
    tier: TestFileTier, 
    name: str = "test.docx"
) -> Path:
    """
    Builds a .docx fixture from a named tier's document/footnotes parts.
    """
    document_xml = read_fixture(tier, "document")
    if document_xml is None:
        raise FileNotFoundError(
            f"No document.xml fixture found for tier {tier.name}."
        )
    footnotes_xml = read_fixture(tier, "footnotes")
    return build_docx(tmp_path, document_xml, footnotes_xml, name)
