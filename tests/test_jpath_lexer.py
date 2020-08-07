from unittest import TestCase

from jpath_finder.jpath_errors import JPathLexerError
from jpath_finder.jpath_lexer import JPathLexer


class TestJPathLexer(TestCase):
    def setUp(self):
        self._lexer = JPathLexer()

    def test_tokenize_error(self):
        pass

    def test_filter_good_path(self):
        path = (
            "$.product[?(@.name.value=='javier' & moved!=true & "
            "this<=false)].other > 2.433 & < 23424"
        )
        expected = [
            ("$", "$"),
            (".", "."),
            ("ID", "product"),
            ("[", "["),
            ("?", "?"),
            ("(", "("),
            ("@", "@"),
            (".", "."),
            ("ID", "name"),
            (".", "."),
            ("ID", "value"),
            ("FILTER_OP", "=="),
            ("STRING", "javier"),
            ("&", "&"),
            ("ID", "moved"),
            ("FILTER_OP", "!="),
            ("BOOL", True),
            ("&", "&"),
            ("ID", "this"),
            ("FILTER_OP", "<="),
            ("BOOL", False),
            (")", ")"),
            ("]", "]"),
            (".", "."),
            ("ID", "other"),
            ("FILTER_OP", ">"),
            ("FLOAT", 2.433),
            ("&", "&"),
            ("FILTER_OP", "<"),
            ("INTEGER", 23424),
        ]
        tokens = self._lexer.tokenize(path)
        for index, token in enumerate(tokens):
            exp = expected[index]
            self.assertEqual(token.type, exp[0])
            self.assertEqual(token.value, exp[1])

    def test_tokenize_good_str(self):
        path = "$.product[0].price"
        expected = [
            ("$", "$"),
            (".", "."),
            ("ID", "product"),
            ("[", "["),
            ("INTEGER", 0),
            ("]", "]"),
            (".", "."),
            ("ID", "price"),
        ]
        tokens = self._lexer.tokenize(path)
        for index, token in enumerate(tokens):
            exp = expected[index]
            self.assertEqual(token.type, exp[0])
            self.assertEqual(token.value, exp[1])

    def test_single_quote(self):
        path = "$.product['items'].price"
        expected = [
            ("$", "$"),
            (".", "."),
            ("ID", "product"),
            ("[", "["),
            ("STRING", "items"),
            ("]", "]"),
            (".", "."),
            ("ID", "price"),
        ]
        tokens = self._lexer.tokenize(path)
        for index, token in enumerate(tokens):
            exp = expected[index]
            self.assertEqual(token.type, exp[0])
            self.assertEqual(token.value, exp[1])

    def test_single_quote_content(self):
        path = "['\\other'].price"
        expected = [
            ("[", "["),
            ("STRING", "other"),
            ("]", "]"),
            (".", "."),
            ("ID", "price"),
        ]
        tokens = self._lexer.tokenize(path)
        for index, token in enumerate(tokens):
            exp = expected[index]
            self.assertEqual(token.type, exp[0])
            self.assertEqual(token.value, exp[1])

    def test_double_quote(self):
        path = '$.product["items"].price[2:6][..]'
        expected = [
            ("$", "$"),
            (".", "."),
            ("ID", "product"),
            ("[", "["),
            ("STRING", "items"),
            ("]", "]"),
            (".", "."),
            ("ID", "price"),
            ("[", "["),
            ("INTEGER", 2),
            (":", ":"),
            ("INTEGER", 6),
            ("]", "]"),
            ("[", "["),
            ("DOUBLEDOT", ".."),
            ("]", "]"),
        ]
        tokens = self._lexer.tokenize(path)
        for index, token in enumerate(tokens):
            exp = expected[index]
            self.assertEqual(token.type, exp[0])
            self.assertEqual(token.value, exp[1])

    def test_double_quote_value(self):
        path = '["\\items"] "show"'
        expected = [("[", "["), ("STRING", "items"), ("]", "]"), ("STRING", "show")]
        tokens = self._lexer.tokenize(path)
        for index, token in enumerate(tokens):
            exp = expected[index]
            self.assertEqual(token.type, exp[0])
            self.assertEqual(token.value, exp[1])

    def test_named_operator(self):
        path = "example.other`nice`[*]"
        expected = [
            ("ID", "example"),
            (".", "."),
            ("ID", "other"),
            ("NAMED_OPERATOR", "nice"),
            ("[", "["),
            ("*", "*"),
            ("]", "]"),
        ]
        tokens = self._lexer.tokenize(path)
        for index, token in enumerate(tokens):
            exp = expected[index]
            self.assertEqual(token.type, exp[0])
            self.assertEqual(token.value, exp[1])

    def test_new_line(self):
        path = "example.other\n.nice\n[-1]\t\n"
        expected = [
            ("ID", "example"),
            (".", "."),
            ("ID", "other"),
            (".", "."),
            ("ID", "nice"),
            ("[", "["),
            ("INTEGER", -1),
            ("]", "]"),
        ]
        tokens = self._lexer.tokenize(path)
        for index, token in enumerate(tokens):
            exp = expected[index]
            self.assertEqual(token.type, exp[0])
            self.assertEqual(token.value, exp[1])

    def test_single_quote_error(self):
        path = "$.show.me'the money"
        with self.assertRaises(JPathLexerError):
            tokens = self._lexer.tokenize(path)
            _ = [token for token in tokens]

    def test_double_quote_erros(self):
        path = '$.\\items"'
        with self.assertRaises(JPathLexerError):
            tokens = self._lexer.tokenize(path)
            _ = [token for token in tokens]

    def test_back_quote_errors(self):
        path = "show.me`the.money"
        with self.assertRaises(JPathLexerError):
            tokens = self._lexer.tokenize(path)
            _ = [token for token in tokens]

    def tokenize(self, j_path):
        with self.assertRaises(JPathLexerError):
            tokens = self._lexer.tokenize(j_path)
            _ = [token for token in tokens]

    def test_basic_errors(self):
        self.tokenize("'\"")
        self.tokenize("\"'")
        self.tokenize('"`')
        self.tokenize('`"')
        self.tokenize("`'")
        self.tokenize('"`')
        self.tokenize("'`")
        self.tokenize("$.show{2:3}[show]asd.ske")
        self.tokenize("$.show['me'']")
        self.tokenize("$.show;:[2,3]")
        self.tokenize("$.foo.bar.#")

    def test_filter_tokenize(self):
        path = "$.[?(@.name)]"
        expected = [
            ("$", "$"),
            (".", "."),
            ("[", "["),
            ("?", "?"),
            ("(", "("),
            ("@", "@"),
            (".", "."),
            ("ID", "name"),
            (")", ")"),
            ("]", "]"),
        ]
        tokens = self._lexer.tokenize(path)
        for index, token in enumerate(tokens):
            exp = expected[index]
            self.assertEqual(token.type, exp[0])
            self.assertEqual(token.value, exp[1])

    def test_filter_tokenize_with_or(self):
        path = "objects_4[?(@.cow=8 & (@.cat=2 | @.cat=3))]"
        expected = [
            ("ID", "objects_4"),
            ("[", "["),
            ("?", "?"),
            ("(", "("),
            ("@", "@"),
            (".", "."),
            ("ID", "cow"),
            ("FILTER_OP", "="),
            ("INTEGER", 8),
            ("&", "&"),
            ("(", "("),
            ("@", "@"),
            (".", "."),
            ("ID", "cat"),
            ("FILTER_OP", "="),
            ("INTEGER", 2),
            ("|", "|"),
            ("@", "@"),
            (".", "."),
            ("ID", "cat"),
            ("FILTER_OP", "="),
            ("INTEGER", 3),
            (")", ")"),
            (")", ")"),
            ("]", "]"),
        ]
        tokens = self._lexer.tokenize(path)
        for index, token in enumerate(tokens):
            exp = expected[index]
            self.assertEqual(token.type, exp[0])
            self.assertEqual(token.value, exp[1])

    def test_integer_math_operator(self):
        path = "3 * 4 + 2 - 4.3 / 2.44"
        expected = [
            ("INTEGER", 3),
            ("*", "*"),
            ("INTEGER", 4),
            ("+", "+"),
            ("INTEGER", 2),
            ("-", "-"),
            ("FLOAT", 4.3),
            ("/", "/"),
            ("FLOAT", 2.44),
        ]
        tokens = self._lexer.tokenize(path)
        for index, token in enumerate(tokens):
            exp = expected[index]
            self.assertEqual(token.type, exp[0])
            self.assertEqual(token.value, exp[1])

    def test_str_math_operator(self):
        path = "foo * bar + other"
        expected = [
            ("ID", "foo"),
            ("*", "*"),
            ("ID", "bar"),
            ("+", "+"),
            ("ID", "other"),
        ]
        tokens = self._lexer.tokenize(path)
        for index, token in enumerate(tokens):
            exp = expected[index]
            self.assertEqual(token.type, exp[0])
            self.assertEqual(token.value, exp[1])

    def test_string_and_math_operator(self):
        path = "'foo' - 'bar' / 'other'"
        expected = [
            ("STRING", "foo"),
            ("-", "-"),
            ("STRING", "bar"),
            ("/", "/"),
            ("STRING", "other"),
        ]
        tokens = self._lexer.tokenize(path)
        for index, token in enumerate(tokens):
            exp = expected[index]
            self.assertEqual(token.type, exp[0])
            self.assertEqual(token.value, exp[1])
