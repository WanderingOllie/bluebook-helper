"""
Extracts word/document.xml (and word/footnotes.xml, if present) from a real
.docx file into tests/files/<tier>/.

Usage:
    uv run python tests/extract_xml.py path/to/source.docx footnote
"""

import argparse
import re
import sys
import zipfile
from helpers import DOCUMENT_PART, FOOTNOTES_PART, FILES_DIR, TestFileTier


def extract(docx_path: str, tier: TestFileTier) -> None:
    with zipfile.ZipFile(docx_path) as z:
        if DOCUMENT_PART not in z.namelist():
            raise FileNotFoundError(f"{docx_path} has no {DOCUMENT_PART}.")
        document_xml = z.read(DOCUMENT_PART)
        footnotes_xml = (
            z.read(FOOTNOTES_PART) if FOOTNOTES_PART in z.namelist() else None
        )

    out_dir = FILES_DIR / tier.name.lower()
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "document.xml").write_bytes(document_xml)
    print(f"Wrote {out_dir / 'document.xml'}")

    if footnotes_xml is not None:
        (out_dir / "footnotes.xml").write_bytes(footnotes_xml)
        print(f"Wrote {out_dir / 'footnotes.xml'}")
    else:
        print(f"{docx_path} has no {FOOTNOTES_PART}, skipping.")

    _warn_on_authorship_metadata(document_xml, footnotes_xml)


def _warn_on_authorship_metadata(*xml_blobs: bytes | None) -> None:
    """Flags w:author values that look like a real name."""
    authors = set()
    for blob in xml_blobs:
        if blob is not None:
            authors.update(re.findall(rb'w:author="([^"]*)"', blob))

    unscrubbed = sorted(
        a.decode("utf-8") for a in authors if a not in (b"", b"Author")
    )
    if unscrubbed:
        print(
            f"WARNING: Found tracked-change author name(s) {unscrubbed} "
            "in the extracted XML.",
            file=sys.stderr,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx_path", help="Path to the source .docx file.")
    parser.add_argument(
        "tier",
        choices=[t.name.lower() for t in TestFileTier],
        help="Which fixture tier to write into (tests/files/<tier>/).",
    )
    args = parser.parse_args()
    extract(args.docx_path, TestFileTier[args.tier.upper()])


if __name__ == "__main__":
    main()
