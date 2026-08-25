from typing import List
from src.extractor.models import CitationSentence, ExtractedDocument
from src.spotter.models import Issue, Rule, RuleRunsOn, SpottedDoc
from src.spotter.rules import ALL_RULES


class Spotter:
    """Walks a document, spotting Issues using Rules."""

    def __init__(
        self, 
        document: ExtractedDocument, 
        rules: List[Rule] = ALL_RULES
    ) -> None:
        self._document = document
        self._rules = rules

    def spot(self) -> SpottedDoc:
        spotted_doc = SpottedDoc(self._document)

        for sentence in self._document.sentences:
            for rule in self._rules:
                spotted_doc.issues.extend(self._run_rule(rule, sentence))

        return spotted_doc

    def _run_rule(self, rule: Rule, sentence: CitationSentence) -> List[Issue]:
        if rule.runs_on is RuleRunsOn.SENTENCE:
            return rule.run(sentence)
        return [
            issue
            for clause in sentence.clauses
            for issue in rule.run(clause)
        ]
