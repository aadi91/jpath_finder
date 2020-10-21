from unittest import TestCase

from jpath_finder.jpath_datum import Datum, ROOT


class TestBaseDatum(TestCase):
    def setUp(self):
        self._data_list = [1, "ab", True, (1, None), {}, tuple()]
        self._data_str = "This is an example to indexing"
        self._data_dict = {
            12: "example str",
            "string key": True,
            False: [],
            2.4: tuple()
        }
        self._indexes = [
            1,
            3,
            5,
            slice(None, None, None),
            slice(0),
            slice(0, 3, 2)
        ]
        self._data_without_index = [
            2.4,
            45,
            True,
        ]

    def test_d_under_getitem_in_list(self):
        datum = Datum(self._data_list)
        for index in self._indexes:
            self.assertEqual(datum[index].value, self._data_list[index])

    def test_d_under_getitem_in_str(self):
        datum = Datum(self._data_str)
        for index in self._indexes:
            self.assertEqual(datum[index].value, self._data_str[index])

    def test_d_under_getitem_in_dict(self):
        datum = Datum(self._data_dict)
        for index in self._data_dict.keys():
            self.assertEqual(datum[index].value, self._data_dict[index])

    def test_d_under_getitem_with_exception(self):
        for data in self._data_without_index:
            datum = Datum(data)
            for index in self._indexes:
                with self.assertRaises(Exception):
                    datum[index]

    def test_str_list(self):
        datum = Datum(self._data_list)
        self.assertEqual(str(datum), ROOT)
        datum = datum[1]
        self.assertEqual(str(datum), "$[1]")

    def test_str_dict(self):
        datum = Datum(self._data_dict)
        self.assertEqual(str(datum), ROOT)
        datum = datum["string key"]
        self.assertEqual(str(datum), "$[string key]")

    def test_list_slice(self):
        datum = Datum(["a", "b", "c", "d"])
        result = [(str(v), v.value) for v in list(datum)[slice(0, 4, 2)]]
        self.assertEqual(result, [("$[0]", "a"), ("$[2]", "c")])

    def test_str_slice(self):
        datum = Datum("This is")
        resp = datum[0:4:2]
        self.assertEqual([(str(resp), resp.value)], [('$[slice(0, 4, 2)]', 'Ti')])

    def test_list_method_in_datum(self):
        expected = ["a", "b", "c", "d"]
        datum = Datum(expected)
        result = [v.value for v in list(datum)]
        self.assertEqual(result, expected)

    def test_type_method(self):
        cases = [int, list, float, bool, dict, tuple]
        for case in cases:
            assert isinstance(Datum(case()), case)
