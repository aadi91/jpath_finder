from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
)

import logging

from ply.lex import TOKEN, lex

from jpath_finder.jpath_errors import JPathLexerError


logger = logging.getLogger(__name__)

# Regex
id_ = r"@?[a-zA-Z_][a-zA-Z0-9_@\-]*"
integer = r"-?\d+"
bool_ = r"true|false"
float_ = r"-?\d+\.\d+"
single_quote = r"'"
single_quote_content = r"[^'\\]+"
single_quote_escape = r"\\."
single_quote_end = r"'"
double_quote = r'"'
double_quote_content = r'[^"\\]+'
double_quote_escape = r"\\."
double_quote_end = r'"'
back_quote = r"`"
back_quote_escape = r"\\."
back_quote_content = r"[^`\\]+"
back_quote_end = r"`"
new_line = r"\n"

ERROR_MESSAGE = "unexpected character '{0}'"
QUOTE_ERROR_MESSAGE = (
    "Error on line {0}, col {1} while lexing {2} field: " "Unexpected character: {3} "
)


class JPathLexer(object):
    """A Lexical analyzer for JsonPath."""

    def __init__(self, debug=False):
        self._debug = debug
        self._lexer = lex(module=self, debug=self._debug, errorlog=logger)

    def _reset_state(self):
        self._lexer.latest_newline = 0
        self._lexer.string_value = ""
        self._lexer.begin("INITIAL")

    def tokenize(self, string):
        """
        Maps a string to an iterator over tokens.
        In other words: [char] -> [token]
        """
        self._reset_state()
        self._lexer.input(string)
        for tok in self._lexer:
            yield tok

        if self._lexer.string_value:
            raise JPathLexerError("Unexpected EOF in string literal or identifier")

    literals = [
        "*",
        ".",
        "[",
        "]",
        "(",
        ")",
        "$",
        ",",
        ":",
        "|",
        "&",
        "?",
        "@",
        "+",
        "/",
        "-",
    ]

    reserved_words = {"where": "WHERE"}

    tokens = [
        "BOOL",
        "DOUBLEDOT",
        "INTEGER",
        "FLOAT",
        "ID",
        "NAMED_OPERATOR",
        "FILTER_OP",
        "STRING",
    ] + list(reserved_words.values())

    states = [
        ("singlequote", "exclusive"),
        ("doublequote", "exclusive"),
        ("backquote", "exclusive"),
    ]

    @staticmethod
    def t_error(t):
        raise JPathLexerError(ERROR_MESSAGE.format(t.value))

    t_DOUBLEDOT = r"\.\."
    t_ignore = " \t"
    t_FILTER_OP = r"==?|<=|>=|!=|<|>"

    @staticmethod
    @TOKEN(bool_)
    def t_BOOL(t):
        t.value = True if t.value == "true" else False
        return t

    @staticmethod
    @TOKEN(float_)
    def t_FLOAT(t):
        t.value = float(t.value)
        return t

    @staticmethod
    @TOKEN(integer)
    def t_INTEGER(t):
        t.value = int(t.value)
        return t

    @staticmethod
    @TOKEN(id_)
    def t_ID(t):
        t.type = JPathLexer.reserved_words.get(t.value, "ID")
        return t

    t_singlequote_ignore = ""

    @staticmethod
    @TOKEN(single_quote)
    def t_singlequote(t):
        t.lexer.string_start = t.lexer.lexpos
        t.lexer.string_value = ""
        t.lexer.push_state("singlequote")

    @staticmethod
    @TOKEN(single_quote_content)
    def t_singlequote_content(t):
        t.lexer.string_value += t.value

    @staticmethod
    @TOKEN(single_quote_escape)
    def t_singlequote_escape(t):
        t.lexer.string_value += t.value[1]

    @staticmethod
    @TOKEN(single_quote_end)
    def t_singlequote_end(t):
        t.value = t.lexer.string_value
        t.type = "STRING"
        t.lexer.string_value = ""
        t.lexer.pop_state()
        return t

    @staticmethod
    def t_singlequote_error(t):
        msg = QUOTE_ERROR_MESSAGE.format(
            t.lexer.lineno,
            t.lexpos - t.lexer.latest_newline,
            "single_quoted",
            t.value[0],
        )
        raise JPathLexerError(msg)

    t_doublequote_ignore = ""

    @staticmethod
    @TOKEN(double_quote)
    def t_doublequote(t):
        t.lexer.string_start = t.lexer.lexpos
        t.lexer.string_value = ""
        t.lexer.push_state("doublequote")

    @staticmethod
    @TOKEN(double_quote_content)
    def t_doublequote_content(t):
        t.lexer.string_value += t.value

    @staticmethod
    @TOKEN(double_quote_escape)
    def t_doublequote_escape(t):
        t.lexer.string_value += t.value[1]

    @staticmethod
    @TOKEN(double_quote_end)
    def t_doublequote_end(t):
        t.value = t.lexer.string_value
        t.type = "STRING"
        t.lexer.string_value = ""
        t.lexer.pop_state()
        return t

    @staticmethod
    def t_doublequote_error(t):
        msg = QUOTE_ERROR_MESSAGE.format(
            t.lexer.lineno,
            t.lexpos - t.lexer.latest_newline,
            "double_quoted",
            t.value[0],
        )
        raise JPathLexerError(msg)

    t_backquote_ignore = ""

    @staticmethod
    @TOKEN(back_quote)
    def t_backquote(t):
        t.lexer.string_start = t.lexer.lexpos
        t.lexer.string_value = ""
        t.lexer.push_state("backquote")

    @staticmethod
    @TOKEN(back_quote_escape)
    def t_backquote_escape(t):
        t.lexer.string_value += t.value[1]

    @staticmethod
    @TOKEN(back_quote_content)
    def t_backquote_content(t):
        t.lexer.string_value += t.value

    @staticmethod
    @TOKEN(back_quote_end)
    def t_backquote_end(t):
        t.value = t.lexer.string_value
        t.type = "NAMED_OPERATOR"
        t.lexer.string_value = ""
        t.lexer.pop_state()
        return t

    @staticmethod
    def t_backquote_error(t):
        msg = QUOTE_ERROR_MESSAGE.format(
            t.lexer.lineno, t.lexpos - t.lexer.latest_newline, "backquoted", t.value[0]
        )
        raise JPathLexerError(msg)

    @staticmethod
    @TOKEN(new_line)
    def t_newline(t):
        t.lexer.lineno += 1
        t.lexer.latest_newline = t.lexpos
