# region List markers
LIST_ITEM_MARKER = '-'
LIST_ITEM_PREFIX = '- '
# endregion

# region Structural characters
COMMA = ','
COLON = ':'
SPACE = ' '
PIPE = '|'
# endregion

# region Brackets and braces
OPEN_BRACKET = '['
CLOSE_BRACKET = ']'
OPEN_BRACE = '{'
CLOSE_BRACE = '}'
# endregion

# region Literals
NULL_LITERAL = 'null'
TRUE_LITERAL = 'true'
FALSE_LITERAL = 'false'
# endregion

# region Escape characters
BACKSLASH = '\\'
DOUBLE_QUOTE = '"'
NEWLINE = '\n'
CARRIAGE_RETURN = '\r'
TAB = '\t'
# endregion

# region Delimiters
DELIMITERS = {
    'comma': COMMA,
    'tab': TAB,
    'pipe': PIPE,
}

DEFAULT_DELIMITER = DELIMITERS['comma']
# endregion
