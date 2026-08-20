from src.parser.models import BasicDocument
from src.refiner.models import *


class Refiner:
    """
    Ingests a BasicDocument, creates a CharList, and returns a RefinedDocument.
    """

    def __init__(self, basic_doc: BasicDocument) -> None:
        self._basic_doc = basic_doc

    def refine(self) -> RefinedDocument:
        blocks = self._basic_doc.get_blocks()
        doc = RefinedDocument(self._basic_doc)

        for block in blocks:
            new_list = CharList(block)
            for run in block.get_runs():
                text = run.get_text()
                for i in range(len(text)):
                    new_char = Character(run, i)
                    new_list.add_char(new_char)
            doc.add_char_list(new_list)
            
        return doc
