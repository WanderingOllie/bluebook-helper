from typing import List
from src.spotter.models import Issue, Rule, RuleRunsOn
from src.extractor.models import CitationClause, CitationSentence


def find_unmatched_parens(text: str) -> List[int]:
    """Returns the string indices of every unmatched '(' or ')' in text."""
    unmatched: List[int] = []
    open_stack: List[int] = []

    for i, ch in enumerate(text):
        if ch == "(":
            open_stack.append(i)
        elif ch == ")":
            if open_stack:
                open_stack.pop()
            else:
                unmatched.append(i)

    unmatched.extend(open_stack)
    return sorted(unmatched)


def check_unclosed_parens(
        target: CitationSentence | CitationClause
        ) -> List[Issue]:
    text = target.text
    chars = target.characters

    return [
        Issue(
            location=target,
            starting_char=chars[i],
            ending_char=None,
            comment="Unmatched '(' or ')'",
        )
        for i in find_unmatched_parens(text)
    ]


UNCLOSED_PARENS = Rule(
    name="unclosed_parens",
    runs_on=RuleRunsOn.SENTENCE,
    check=check_unclosed_parens,
)

ALL_RULES = [UNCLOSED_PARENS]
