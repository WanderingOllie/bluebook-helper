from typing import cast
import zipfile
from lxml import etree
from src.parser.models import Block, BasicDocument, RunView, BlockType, RunType, DOCX_NS

DOCUMENT_PART = "word/document.xml"
FOOTNOTES_PART = "word/footnotes.xml"


class Parser:
    """Parses a .docx file into a Document of ordered Blocks and RunViews."""

    def __init__(self, path: str) -> None:
        with zipfile.ZipFile(path) as z:
            self._document_tree = etree.fromstring(z.read(DOCUMENT_PART))
            self._footnotes_tree = (
                etree.fromstring(z.read(FOOTNOTES_PART))
                if FOOTNOTES_PART in z.namelist()
                else None
            )
        self._run_counter = 0
        self._block_counter = 0

    def parse(self) -> BasicDocument:
        """Parse the document body into a Document of ordered Blocks."""
        document = BasicDocument()
        runs = self._document_tree.findall(".//w:r", DOCX_NS)
        self._walk_runs(runs, BlockType.PARAGRAPH, document)
        return document

    def _walk_runs(
        self, runs: list[etree._Element], block_type: BlockType, document: BasicDocument
    ) -> None:
        """Walk a sequence of runs, splitting into blocks on footnote refs."""
        current_block = Block(self._next_block_order(), block_type)

        for run in runs:
            run_view = RunView(run, self._next_run_order())
            current_block.runs.append(run_view)

            if run_view.type is RunType.FOOTNOTE_REF:
                document.blocks.append(current_block)
                self._parse_footnote(run_view.footnote_id, document)
                current_block = Block(self._next_block_order(), block_type)

        if current_block.runs:
            document.blocks.append(current_block)

    def _parse_footnote(self, footnote_id: str, document: BasicDocument) -> None:
        """Look up a footnote by id in footnotes.xml and parse its content."""
        if self._footnotes_tree is None:
            return

        matches = cast(
            list[etree._Element],
            self._footnotes_tree.xpath(
                f'.//w:footnote[@w:id="{footnote_id}"]', namespaces=DOCX_NS
            ),
        )
        if not matches:
            return

        runs = matches[0].findall(".//w:r", DOCX_NS)
        self._walk_runs(runs, BlockType.FOOTNOTE, document)

    def _next_run_order(self) -> int:
        order = self._run_counter
        self._run_counter += 1
        return order

    def _next_block_order(self) -> int:
        order = self._block_counter
        self._block_counter += 1
        return order
