import json
import os
import sys

from unittest import TestCase

import pytest

from mock import MagicMock

from tests.parser_mix_cases import BASIC_PATH_CASE, DESCENDANT_PATH_CASE
from tests.parser_original_cases import (
    ARITHMETIC_CASES,
    FILTER_CASES,
    LEN_CASES,
    SORTED_CASES,
)
from tests.parser_test_cases import PATH_CASES, STR_REPR_CASES
from jpath_finder.jpath_errors import JPathNodeError, JPathError
from jpath_finder.jpath_parser import BasicLogger, JsonPathParser, StaticParser, find, parse


class TestJsonPathParser(TestCase):
    def setUp(self):
        self._parser = JsonPathParser(debug=False)
        self._abs_path = os.path.abspath("tests/json_for_test.json")
        self._file = open(self._abs_path, "r")
        self._data = json.load(self._file)

    def find(self, path):
        parsed = self._parser.parse(path)
        return parsed.find(self._data)

    def test_parse(self):
        self.assertEqual(self.find("$.name"), ["data"])
        self.assertEqual(self.find("$.names"), [])

    def test_parser_dict_many(self):
        self.assertEqual(self.find("$.data_2.name,age"), ["jhon", 23])

    def test_parser_list_all(self):
        self.assertEqual(
            self.find("$.data_1.names[*]"), [{"name": "carlos"}, {"name": "pepe"}]
        )
        self.assertEqual(self.find("$.data_1.names[*].name"), ["carlos", "pepe"])
        self.assertEqual(
            self.find("data_1.names[*]"), [{"name": "carlos"}, {"name": "pepe"}]
        )
        self.assertEqual(self.find("data_1.names[*].name"), ["carlos", "pepe"])

    def test_slice(self):
        self.assertEqual(self.find("$.data_4.list_items[2:4]"), ["item_3", "item_4"])
        self.assertEqual(self.find("$.data_4.list_items[-1]"), ["item_8"])
        self.assertEqual(
            self.find("$.data_4.list_items[5:]"), ["item_6", "item_7", "item_8"]
        )
        self.assertEqual(self.find("$.list_items_2[:]"), ["item_1", "item_2"])
        self.assertEqual(self.find("$.list_items_2[*]"), ["item_1", "item_2"])
        self.assertEqual(self.find("$.list_items_2[0::3]"), ["item_1"])
        self.assertEqual(self.find("$.data[0].attributes.info.links.self[32:42]"), ["[number]=3"])

    def test_slice_many_values(self):
        expected = [
            3.0,
            261.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            500.0,
        ]
        self.assertEqual(self.find("$.items[*].quotas[*].usage"), expected)

        expected = [40960.0, 20480.0, 40960.0, 20480.0, 90.0, 2040.0, 80.0, 20480.0]
        self.assertEqual(self.find("$.items[*].quotas[?(@.limit>72)].limit"), expected)

    def test_index(self):
        self.assertEqual(self.find("$.data_4.list_items[0]"), ["item_1"])
        self.assertEqual(self.find("$.data_4.list_items[-1]"), ["item_8"])
        self.assertEqual(self.find("$.list_items.[0]"), ["item_1"])
        self.assertEqual(self.find("$.list_items[2:4]"), ["item_3", "item_4"])

    def test_fields(self):
        self.assertEqual(self.find("$.data_6..list_items[name]"), ["jhon"])
        self.assertEqual(self.find("$.data_6.[count]"), [1])

    @pytest.mark.skipif(
        sys.version_info < (3, 0), reason="Py2 return the dict values in other order"
    )
    def test_all_index(self):
        self.assertEqual(self.find("$.data_6.list_items[*]"), ["jhon", "wick"])

    @pytest.mark.skipif(
        sys.version_info < (3, 0), reason="string unicode repr diff py2 and 3"
    )
    def test_fields_many_fields(self):
        self.assertEqual(self.find("$.data_7.list_items[age,live]"), [34, True])
        self.assertEqual(
            self.find("$.data_7.list_items.[*]"), ["jhon", "wick", 34, "male", True]
        )

    def test_descendants(self):
        self.assertEqual(self.find("$.data_3.items..price"), [12, 32])

    def test_unions(self):
        self.assertEqual(self.find("$.data_3.items.products[*].other|price"), [12, 32])
        self.assertEqual(
            self.find("$.data_3.items.products[*].name|price"),
            ["dishes", 12, "spon", 32],
        )

    def test_where(self):
        expected = [{"name": "dishes", "price": 12}, {"name": "spon", "price": 32}]
        self.assertEqual(self.find("$.data_3.items.products[*] where name"), expected)

    def test_len(self):
        self.assertEqual(self.find("$.data_3.items.products.`len`"), [2])
        self.assertEqual(self.find("$.data_3.items.`len`"), [4])
        self.assertEqual(self.find("$.data_3.items.id_str.`len`"), [5])
        self.assertEqual(self.find("$.data_2.`len`"), [3])

    def test_sum(self):
        self.assertEqual(self.find("$.data_4.machines.cpu.`sum`"), [19])
        self.assertEqual(round(self.find("$.data_4.machines.ram.`sum`")[0], 2), 11.63)

        with self.assertRaises(JPathNodeError):
            self.find("$.data_4.machines.name.`sum`")

    def test_avg(self):
        self.assertEqual(round(self.find("$.data_4.machines.cpu.`avg`")[0], 2), 6.33)
        self.assertEqual(round(self.find("$.data_4.machines.ram.`avg`")[0], 2), 3.88)

        with self.assertRaises(JPathNodeError):
            self.find("$.data_4.machines.name.`avg`")

    @pytest.mark.skipif(
        sys.version_info < (3, 0), reason="string unicode repr diff py2 and 3"
    )
    def test_multi_parse(self):
        for path, result, parsed_str, parsed_repr in PATH_CASES:
            parsed = self._parser.parse(path)
            assert str(parsed) == parsed_str
            assert repr(parsed) == parsed_repr
            self.assertEqual(self.find(path), result)

    @pytest.mark.skipif(
        sys.version_info < (3, 0), reason="string unicode repr diff py2 and 3"
    )
    def test_filter_multi_cases(self):
        for path, parsed_str, parsed_repr in STR_REPR_CASES:
            parsed = self._parser.parse(path)
            assert str(parsed) == parsed_str
            assert repr(parsed) == parsed_repr

    def test_filter_with_good_path(self):
        path = "$.data_5.virtual_machines[?(@.ram==2.2)].name"
        self.assertEqual(self.find(path), ["Unix"])

        path = "$.data_5.virtual_machines[?(@.ram)].name"
        self.assertEqual(self.find(path), ["Linux", "Windows", "Unix"])

        path = "$.data_5.virtual_machines[?(@.ram==2.2 & @.cpu==4)].name"
        self.assertEqual(self.find(path), [])

    @pytest.mark.skipif(
        sys.version_info < (3, 0), reason="The method 'assertRaisesRegex' does not exist in python2"
    )
    def test_error(self):
        message = "JPathLexerError: unexpected character '%'"
        with self.assertRaisesRegex(JPathError, message):
            _ = self._parser.parse("$.%")

        message = "JPathParseError: Unable to parse the string ','"
        with self.assertRaisesRegex(JPathError, message):
            _ = self._parser.parse("$.objects[2,3].name")

    def tearDown(self):
        self._file.close()


class TestJPathParserOriginalCases(TestCase):
    def setUp(self):
        self._parser = JsonPathParser(debug=False)
        self._abs_path = os.path.abspath("tests/json_for_test.json")
        self._file = open(self._abs_path, "r")
        self._data = json.load(self._file)

    def find(self, path):
        parsed = self._parser.parse(path)
        return parsed.find(self._data)

    def test_original_sorted(self):
        for path, expected in SORTED_CASES:
            self.assertEqual(self.find(path), expected)

    def test_original_len(self):
        for path, expected in LEN_CASES:
            self.assertEqual(self.find(path), expected)

    def test_original_filter(self):
        for path, expected in FILTER_CASES:
            self.assertEqual(self.find(path), expected)

    @pytest.mark.skipif(
        sys.version_info < (3, 0), reason="string unicode repr diff py2 and 3"
    )
    def test_original_arithmetic(self):
        for path, p_str, p_repr, exp in ARITHMETIC_CASES:
            parsed = self._parser.parse(path)
            self.assertEqual(str(parsed), p_str)
            self.assertEqual(repr(parsed), p_repr)
            self.assertEqual(parsed.find(self._data), exp)

    def tearDown(self):
        self._file.close()


class TestMixCases(TestCase):
    def setUp(self):
        self._parser = JsonPathParser(debug=False)
        self._abs_path = os.path.abspath("tests/json_for_test.json")
        self._file = open(self._abs_path, "r")
        self._data = json.load(self._file)

    def find(self, path):
        parsed = self._parser.parse(path)
        return parsed.find(self._data)

    def test_basic_path_case_without_root(self):
        for path, expected in BASIC_PATH_CASE:
            self.assertEqual(self.find(path), expected)

    @pytest.mark.skipif(
        sys.version_info < (3, 0), reason="string unicode repr diff py2 and 3"
    )
    def test_descendant_without_root(self):
        for path, expected in DESCENDANT_PATH_CASE:
            self.assertEqual(self.find(path), expected)


class TestStaticParser(TestCase):
    def test_find(self):
        self.assertEqual(str(StaticParser.parse("$.name")), "$.name")


class TestBasicLogger(TestCase):
    def test_debug(self):
        self.assertEqual(BasicLogger.debug("message"), None)


class TestMethods(TestCase):
    def test_parse_method(self):
        self.assertEqual(str(parse("name.value")), "name.value")

    def test_find_method(self):
        self.assertEqual(find("name", {"name": "Json"}), ["Json"])

    def test_find_with_error(self):
        logger = MagicMock()
        self.assertEqual(find("[3]", [], logger=logger, debug=True), [])
        logger.debug.assert_called_once_with(
            "JPathIndexError: Invalid Index [3] for []"
        )

    def test_find_with_error_no_log(self):
        logger = MagicMock()
        self.assertEqual(find("[3]", [], logger=logger), [])
        logger.debug.assert_not_called()
