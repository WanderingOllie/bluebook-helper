from src.parser.models import BasicDocument
from src.refiner.models import RefinedDocument


class Refiner:
    """Ingests a BasicDocument and produces a RefinedDocument of Characters."""

    def __init__(self, basic_doc: BasicDocument) -> None:
        self._basic_doc = basic_doc

    def refine(self) -> RefinedDocument:
        doc = RefinedDocument(self._basic_doc)

        for block in doc.blocks:
            doc.char_map[block] = [
                char for run in block.runs for char in run.characters
            ]

        return doc
