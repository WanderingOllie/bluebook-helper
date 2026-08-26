from builders import sentence_from_text
from src.spotter.rules.generic import UnclosedParens

# ------ UnclosedParens ------
def test_unclosed_parens_missing_closing():
    sentence = sentence_from_text("(I'm missing my closing")
    issues = UnclosedParens().check(target=sentence)

    assert len(issues) == 1

    issue = issues[0]
    assert issue.location is sentence
    assert issue.starting_char is sentence.characters[0]
    assert issue.ending_char is None

def test_unclosed_parens_missing_opening():
    sentence = sentence_from_text("I'm missing my opening) - oops")
    issues = UnclosedParens().check(target=sentence)

    assert len(issues) == 1

    issue = issues[0]
    assert issue.location is sentence
    assert issue.starting_char is sentence.characters[22]
    assert issue.ending_char is None

def test_unclosed_parens_nested():
    sentence = sentence_from_text("I have) a (nested set( of issues)")
    issues = UnclosedParens().check(target=sentence)

    assert len(issues) == 2
    assert issues[0].starting_char is sentence.characters[6]
    assert issues[1].starting_char is sentence.characters[10]

def test_unclosed_parens_no_issue():
    sentence = sentence_from_text("I'm a perfect example (truly)")
    issues = UnclosedParens().check(target=sentence)
    assert len(issues) == 0
