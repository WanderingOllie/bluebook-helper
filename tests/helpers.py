from enum import Enum, auto
from pathlib import Path
import zipfile

DOCUMENT_PART = "word/document.xml"
FOOTNOTES_PART = "word/footnotes.xml"

FILES_DIR = Path(__file__).parent / "files"

class TestFileTier(Enum):
    __test__ = False     # not a pytest test class

    BASIC = auto()       # most basic case (prose, in-text cites, no footnotes)
    FOOTNOTE = auto()    # basic case plus foonotes
    COMPLEX = auto()     # footnote case plus comments and tracked changes

    UTIL = auto()        # small, purpose-built stuff for testing one behavior

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


def fixture_dir(tier: TestFileTier, name: str | None = None) -> Path:
    """
    Resolves the on-disk directory holding a fixture's XML parts.
    """
    if tier is TestFileTier.UTIL:
        if not name:
            raise ValueError(
                "UTIL fixtures are named, e.g. "
                'fixture_dir(TestFileTier.UTIL, name="split_on_footnote").'
            )
        return FILES_DIR / "util" / name
    if name:
        raise ValueError(
            f"Name is only used with TestFileTier.UTIL; got name={name} "
            f"for tier {tier.name}."
        )
    return FILES_DIR / tier.name.lower()


def read_fixture(
    tier: TestFileTier, part: str = "document", name: str | None = None
) -> str | None:
    """
    Reads a fixture XML part for a tier (pass `name` for a UTIL scenario).
    """
    path = fixture_dir(tier, name) / f"{part}.xml"
    return path.read_text(encoding="utf-8") if path.exists() else None


def build_tier_docx(
    tmp_path: Path,
    tier: TestFileTier,
    name: str | None = None,
    docx_name: str = "test.docx",
) -> Path:
    """
    Builds a .docx fixture from a tier's (or named UTIL scenario's)
    document/footnotes parts.
    """
    document_xml = read_fixture(tier, "document", name)
    if document_xml is None:
        label = f"UTIL/{name}" if tier is TestFileTier.UTIL else tier.name
        raise FileNotFoundError(f"No document.xml fixture found for {label}.")
    footnotes_xml = read_fixture(tier, "footnotes", name)
    return build_docx(tmp_path, document_xml, footnotes_xml, docx_name)
