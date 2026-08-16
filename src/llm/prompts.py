from openai.types.responses import ResponseInputItemParam


CITATION_SENTENCE_SYSTEM_PROMPT = (
    "You are assisting with Bluebook legal citation analysis. A citation "
    "sentence is one or more citation clauses, separated by semicolons, "
    "that together support a single textual proposition and end with a "
    "period. Given a block of text, return every citation sentence it "
    "contains, in the order they appear, each copied verbatim. Do not "
    "paraphrase, summarize, or alter any characters. A block may contain "
    "zero, one, or several citation sentences."
)

CITATION_CLAUSE_SYSTEM_PROMPT = (
    "You are assisting with Bluebook legal citation analysis. A citation "
    "clause is a single citation to one authority within a citation "
    "sentence. Given a block of text, return every citation clause it "
    "contains, in the order they appear, each copied verbatim. Do not "
    "paraphrase, summarize, or alter any characters. A citation sentence "
    "may contain one or several citation clauses, separated by "
    "semicolons."
)

CITATION_SENTENCE_EXAMPLES: list[ResponseInputItemParam] = [
    {
        "role": "user",
        "content": (
            "TEXT:\nCongress responded directly to this gap. 18 U.S.C. "
            "§ 242 (2018). Commentators have since debated its scope."
        ),
    },
    {
        "role": "assistant",
        "content": '{"items": ["18 U.S.C. § 242 (2018)."]}',
    },
    {
        "role": "user",
        "content": (
            "TEXT:\nThe Court's holding rests on equal protection "
            "grounds. See Brown v. Bd. of Educ., 347 U.S. 483, 495 "
            "(1954); see also Bolling v. Sharpe, 347 U.S. 497 (1954) "
            "(applying the same principle to the District of Columbia). "
            "Congress later codified a parallel rule. 18 U.S.C. § 242 "
            "(2018). Commentators have since debated its scope."
        ),
    },
    {
        "role": "assistant",
        "content": (
            '{"items": ['
            '"See Brown v. Bd. of Educ., 347 U.S. 483, 495 (1954); see '
            'also Bolling v. Sharpe, 347 U.S. 497 (1954) (applying the '
            'same principle to the District of Columbia).", '
            '"18 U.S.C. § 242 (2018)."'
            ']}'
        ),
    },
]

CITATION_CLAUSE_EXAMPLES: list[ResponseInputItemParam] = [
    {
        "role": "user",
        "content": "TEXT:\n18 U.S.C. § 242 (2018).",
    },
    {
        "role": "assistant",
        "content": '{"items": ["18 U.S.C. § 242 (2018)"]}',
    },
    {
        "role": "user",
        "content": (
            "TEXT:\nSee Brown v. Bd. of Educ., 347 U.S. 483, 495 (1954); "
            "see also Bolling v. Sharpe, 347 U.S. 497 (1954) (applying "
            "the same principle to the District of Columbia)."
        ),
    },
    {
        "role": "assistant",
        "content": (
            '{"items": ['
            '"Brown v. Bd. of Educ., 347 U.S. 483, 495 (1954)", '
            '"Bolling v. Sharpe, 347 U.S. 497 (1954)"'
            ']}'
        ),
    },
]
