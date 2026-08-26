from src.extractor.models import CitationSentence
from src.spotter.models import Issue, Rule, RuleRunsOn
from src.spotter.spotter import Spotter
from builders import clause_from_text, sentence_from_text


class _FakeExtractedDoc:
    """Minimal stand-in for ExtractedDocument."""

    def __init__(self, sentences):
        self.blocks = []
        self.sentences = sentences


class _FlagIfContains(Rule):
    name = "flag_if_contains"
    runs_on = RuleRunsOn.SENTENCE

    def __init__(self, needle: str):
        self._needle = needle

    def check(self, target) -> list[Issue]:
        if self._needle not in target.text:
            return []
        return [
            Issue(
                location=target,
                starting_char=target.characters[0],
                ending_char=None,
                comment="flagged",
            )
        ]


class _FlagLeadingParen(Rule):
    name = "flag_leading_paren"
    runs_on = RuleRunsOn.CLAUSE

    def check(self, target) -> list[Issue]:
        if not target.text.startswith("("):
            return []
        return [
            Issue(
                location=target,
                starting_char=target.characters[0],
                ending_char=None,
                comment="flagged",
            )
        ]


def test_spot_collects_issues_from_sentence_scoped_rule():
    sentence = sentence_from_text("flag me please")
    extracted_doc = _FakeExtractedDoc([sentence])

    spotted_doc = Spotter(extracted_doc, rules=[_FlagIfContains("flag me")]).spot()

    assert len(spotted_doc.issues) == 1
    assert spotted_doc.issues[0].location is sentence


def test_spot_finds_nothing_when_no_rule_matches():
    sentence = sentence_from_text("nothing to see here")
    extracted_doc = _FakeExtractedDoc([sentence])

    spotted_doc = Spotter(extracted_doc, rules=[_FlagIfContains("flag me")]).spot()

    assert spotted_doc.issues == []


def test_spot_runs_clause_scoped_rules_once_per_clause():
    sentence = CitationSentence(
        clauses=[clause_from_text("(bad"), clause_from_text("good")]
    )
    extracted_doc = _FakeExtractedDoc([sentence])

    spotted_doc = Spotter(extracted_doc, rules=[_FlagLeadingParen()]).spot()

    assert len(spotted_doc.issues) == 1
    assert spotted_doc.issues[0].location is sentence.clauses[0]


def test_spotted_doc_propagates_blocks_and_sentences():
    sentence = sentence_from_text("Smith v. Jones, 347 U.S. 483 (1954).")
    extracted_doc = _FakeExtractedDoc([sentence])

    spotted_doc = Spotter(extracted_doc, rules=[]).spot()

    assert spotted_doc.sentences == [sentence]
    assert spotted_doc.blocks == []
