from __future__ import absolute_import, division, generators, nested_scopes, print_function

import logging

from ply.yacc import yacc

from jpath_finder.jpath_errors import JPathError, JPathParseError
from jpath_finder.jpath_lexer import JPathLexer
from jpath_finder.jpath_nodes import (
    BINARY_OP_MAP,
    BOOLEAN_OPERATOR_MAP,
    NAMED_OPERATOR_MAP,
    ROOT_MAP,
    AllIndex,
    Child,
    Expression,
    Fields,
    Filter,
    Index,
    NodesFactory,
    Slice,
)


logger = logging.getLogger(__name__)


class JsonPathParser(object):
    """An LA-LR parser for JsonPath"""

    tokens = JPathLexer.tokens

    def __init__(self, debug=False):
        self._debug = debug
        self._lexer = JPathLexer(self._debug)
        self._parser = yacc(
            module=self, debug=self._debug, errorlog=logger, write_tables=False
        )

    def parse(self, string):
        tokens = self._lexer.tokenize(string)
        return self._parser.parse(lexer=TokenIterator(tokens))

    # ===================== PLY Parser specification =====================
    precedence = [
        ("left", "+", "-"),
        ("left", "*", "/"),
        ("left", ","),
        ("left", "STRING", "DOUBLEDOT"),
        ("left", "."),
        ("left", "|"),
        ("left", "&"),
        ("left", "WHERE"),
        ("nonassoc", "ID"),
    ]

    @staticmethod
    def p_error(t):
        msg = "Unable to parse the string '{0}'".format(t.value)
        raise JPathParseError(msg)

    @staticmethod
    def p_child(p):
        """json_path : json_path '.' json_path
                     | json_path '[' index ']'"""
        p[0] = Child(p[1], p[3])

    @staticmethod
    def p_json_path_bin_op(p):
        """json_path : json_path binary_op json_path"""
        p[0] = BINARY_OP_MAP[p[2]](p[1], p[3])

    @staticmethod
    def p_json_path_index(p):
        """json_path : '[' index ']'"""
        p[0] = p[2]

    @staticmethod
    def p_index_expressions(p):
        """index : '?' expressions"""
        p[0] = Filter(p[2])

    @staticmethod
    def p_expression_boolean_operator(p):
        """expressions : expressions boolean_op expressions"""
        p[0] = BOOLEAN_OPERATOR_MAP[p[2]](p[1], p[3])

    @staticmethod
    def p_expression(p):
        """expression : json_path
                      | json_path FILTER_OP jp_object"""
        if len(p) == 2:
            p[0] = Expression(p[1])
        else:
            p[0] = Expression(p[1], p[2], p[3])

    @staticmethod
    def p_expressions_parens_expressions(p):
        """expressions : '(' expressions ')'"""
        p[0] = p[2]

    @staticmethod
    def p_expressions_expression(p):
        """expressions : expression"""
        p[0] = p[1]

    @staticmethod
    def p_json_path_named_operator(p):
        """json_path : NAMED_OPERATOR"""
        p[0] = NAMED_OPERATOR_MAP[p[1]]()

    @staticmethod
    def p_json_path_mat_expression(p):
        """json_path : INTEGER operator INTEGER
                     | STRING operator INTEGER
                     | INTEGER operator STRING
                     | STRING operator STRING
                     | STRING operator json_path
                     | json_path operator STRING
                     | INTEGER operator json_path
                     | json_path operator json_path
                     | json_path operator INTEGER"""
        p[0] = NodesFactory.mat_operator(p[1], p[3], p[2])

    @staticmethod
    def p_operator(p):
        """operator : '+'
                    | '-'
                    | '*'
                    | '/'
        """
        p[0] = p[1]

    @staticmethod
    def p_json_path_parens(p):
        """json_path : '(' json_path ')'"""
        p[0] = p[2]

    @staticmethod
    def p_json_path_fields(p):
        """json_path : fields"""
        p[0] = Fields(*p[1])

    @staticmethod
    def p_index_fields(p):
        """index : fields"""
        p[0] = Fields(*p[1])

    @staticmethod
    def p_fields_id(p):
        """fields : ID"""
        p[0] = [p[1]]

    @staticmethod
    def p_fields_comma(p):
        """fields : fields ',' fields"""
        p[0] = p[1] + p[3]

    @staticmethod
    def p_idx(p):
        """index : INTEGER"""
        p[0] = Index(p[1])

    @staticmethod
    def p_slice_any(p):
        """index : '*'"""
        p[0] = AllIndex()

    @staticmethod
    def p_slice(p):
        """index : int_empty ':' int_empty ':' int_empty
                 | int_empty ':' int_empty"""
        if len(p) == 6:
            p[0] = Slice(start=p[1], end=p[3], step=p[5])
        else:
            p[0] = Slice(start=p[1], end=p[3])

    @staticmethod
    def p_int_empty(p):
        """int_empty : INTEGER
                     | empty"""
        p[0] = p[1]

    @staticmethod
    def p_binary_op(p):
        """binary_op : DOUBLEDOT
                     | '|'
                     | '&'
                     | WHERE"""
        p[0] = p[1]

    @staticmethod
    def p_jp_object(p):
        """jp_object : FLOAT
                     | INTEGER
                     | BOOL
                     | STRING"""
        p[0] = p[1]

    @staticmethod
    def p_json_path_root(p):
        """json_path : '$'
                     | '@'
        """
        p[0] = ROOT_MAP[p[1]]()

    @staticmethod
    def p_boolean_op(p):
        """boolean_op : '|'
                      | '&'"""
        p[0] = p[1]

    @staticmethod
    def p_empty(p):
        """empty :"""
        pass


class TokenIterator(object):
    def __init__(self, iterator):
        self._iterator = iterator

    def token(self):
        try:
            return next(self._iterator)
        except StopIteration:
            return None


class StaticParser(object):
    PARSER = JsonPathParser()

    @staticmethod
    def parse(path):
        """
        :param path: The string JsonPath to be parsed.
        :return: The class tree parsed from the string.
        """
        return StaticParser.PARSER.parse(path)


class BasicLogger(object):
    @staticmethod
    def debug(message):
        """
        :param message: The debug message to be printed in the console.
        :return:
        """
        print(message)


def parse(path):
    """
    :param path: The string JsonPath to be parsed.
    :return: The class tree parsed from the string.
    """
    return StaticParser.parse(path)


def find(path, data, logger=BasicLogger, debug=False):
    """
    :param path: The string JsonPath to be parsed.
    :param data: The json data generally a dictionary.
    :param logger: Logger class with a debug method, like logger.debug(error_message).
    :param debug: True if the logger's debug method will be called. default False.
    :return: A list with the results found.
    """
    try:
        parsed = parse(path)
        return parsed.find(data)
    except JPathError as e:
        if debug:
            message = str(e)
            logger.debug(message)
        return []
