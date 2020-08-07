from unittest import TestCase

from jpath_finder.jpath_errors import (
    JPathError,
    JPathIndexError,
    JPathLexerError,
    JPathNodeError,
    JPathParseError,
)


class TestJPathError(TestCase):
    def test_str(self):
        error = JPathError("unexpected str")
        self.assertEqual(str(error), "JPathError: unexpected str")


class TestJPathLexerError(TestCase):
    def test_str(self):
        error = JPathLexerError("unexpected character")
        self.assertEqual(str(error), "JPathLexerError: unexpected character")


class TestJPathParseError(TestCase):
    def test_str(self):
        error = JPathParseError("some error")
        self.assertEqual(str(error), "JPathParseError: some error")

        error_2 = JPathParseError("other", "message")
        self.assertEqual(str(error_2), "JPathParseError: other message")


class TestJPathNodeError(TestCase):
    def test_str(self):
        error = JPathNodeError("[*]", {"a": 2})
        self.assertEqual(str(error), "JPathNodeError: Invalid Path [*] for {'a': 2}")


class TestJPathIndexError(TestCase):
    def test_str(self):
        error = JPathIndexError("[2]", {"a": 2})
        self.assertEqual(str(error), "JPathIndexError: Invalid Index [2] for {'a': 2}")
