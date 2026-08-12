from enum import Enum

# ----- PARSER STUFF -----
DOCX_NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
}

class RunType(Enum):
    # Ordinary run
    TEXT = 0

    # Whitespace / character elements
    TAB_CHAR = 1
    LINE_BREAK = 2
    CARRIAGE_RETURN = 3
    NON_BREAKING_HYPHEN = 4
    OPTIONAL_HYPHEN = 5

    # Reference markers
    FOOTNOTE_REF = 6
    ENDNOTE_REF = 7
    COMMENT_REF = 8

RUN_TYPE_MAP = {
    "w:tab": RunType.TAB_CHAR,
    "w:br": RunType.LINE_BREAK,
    "w:cr": RunType.CARRIAGE_RETURN,
    "w:noBreakHyphen": RunType.NON_BREAKING_HYPHEN,
    "w:softHyphen": RunType.OPTIONAL_HYPHEN,
    "w:footnoteReference": RunType.FOOTNOTE_REF,
    "w:endnoteReference": RunType.ENDNOTE_REF,
    "w:commentReference": RunType.COMMENT_REF,
}

class BlockType(Enum):
    PARAGRAPH = 1
    FOOTNOTE = 2
