import sys

from unittest import TestCase

import pytest

from jpath_finder.jpath_errors import JPathIndexError, JPathNodeError
from jpath_finder.jpath_nodes import (
    OPERATOR_MAP,
    AllIndex,
    And,
    Avg,
    Child,
    Descendants,
    Expression,
    Fields,
    Filter,
    Index,
    Leaf,
    Len,
    Node,
    Operator,
    Or,
    Recursive,
    Root,
    Slice,
    Sorted,
    Sum,
    This,
    Union,
    Where,
)


def find(parsed, data):
    return parsed.find(data)


class TestLeaf(TestCase):
    def setUp(self):
        self._leaf = Leaf()
        self._data = {"data": [{"name": "jorge"}, {"name": "james"}]}

    def test_find(self):
        self.assertEqual(self._leaf.find(self._data), None)

    def test_str_and_repr(self):
        self.assertEqual(str(self._leaf), "")
        self.assertEqual(repr(self._leaf), "")

    def test_str_all_leaf(self):
        self.assertEqual(str(Root()), "$")
        self.assertEqual(str(This()), "@")
        self.assertEqual(str(Index(1)), "[1]")
        self.assertEqual(str(Index("*")), "[*]")
        self.assertEqual(str(AllIndex()), "[*]")
        self.assertEqual(str(Fields("name", "other")), "name,other")
        self.assertEqual(str(Fields("name")), "name")
        self.assertEqual(str(Slice(0, 3, 2)), "[0:3:2]")
        self.assertEqual(str(Slice()), "[::]")
        self.assertEqual(str(Len()), "`len`")
        self.assertEqual(str(Sum()), "`sum`")
        self.assertEqual(str(Avg()), "`avg`")
        self.assertEqual(str(Sorted()), "`sorted`")
        self.assertEqual(str(And(Fields("name"), Fields("id"))), "name&id")
        self.assertEqual(str(Or(Fields("name"), Fields("id"))), "name|id")

    def test_repr_all_leaf(self):
        self.assertEqual(repr(Root()), "Root()")
        self.assertEqual(repr(This()), "This()")
        self.assertEqual(repr(Index(2)), "Index(2)")
        self.assertEqual(repr(AllIndex()), "AllIndex()")
        self.assertEqual(repr(Fields("name", "other")), "Fields('name','other')")
        self.assertEqual(repr(Slice(0, 3, 2)), "Slice(start=0,end=3,step=2)")
        self.assertEqual(repr(Len()), "Len()")
        self.assertEqual(repr(Sum()), "Sum()")
        self.assertEqual(repr(Avg()), "Avg()")
        self.assertEqual(repr(Sorted()), "Sorted()")
        self.assertEqual(
            repr(And(Fields("name"), Fields("id"))), "And(Fields('name'),Fields('id'))"
        )
        self.assertEqual(
            repr(Or(Fields("name"), Fields("id"))), "Or(Fields('name'),Fields('id'))"
        )


class TestNode(TestCase):
    def setUp(self):
        self._data = {"data": [{"name": "jorge"}, {"name": "james"}]}

    def test_abstract_methods(self):
        self.assertEqual(Node(None, None).find(self._data), None)

    def test_str_all_nodes(self):
        self.assertEqual(str(Node(None, None)), "")
        self.assertEqual(str(Child(Root(), Fields("name"))), "$.name")
        self.assertEqual(str(Where(Root(), Fields("name"))), "$ where name")
        self.assertEqual(str(Descendants(Root(), Fields("name"))), "$..name")
        self.assertEqual(str(Union(Root(), Fields("name"))), "$|name")

    def test_repr_all_nodes(self):
        self.assertEqual(repr(Node(None, None)), "")
        self.assertEqual(
            repr(Child(Root(), Fields("name"))), "Child(Root(), Fields('name'))"
        )
        self.assertEqual(
            repr(Descendants(Root(), Fields("name"))),
            "Descendants(Root(), Fields('name'))",
        )
        self.assertEqual(
            repr(Union(Root(), Fields("name"))), "Union(Root()|Fields('name'))"
        )

    def test_node_not_equals(self):
        assert not Root() == This()
        assert not This() == Index(2)
        assert not Index(2) == Root()
        assert not Len() == Avg()
        assert not Sum() == Len()
        assert not Avg() == Sorted()
        assert not Sorted() == Sum()
        assert not And(Root(), Fields("name")) == And(Root(), Fields("other"))
        assert not Or(Root(), Fields("name")) == Or(Root(), Fields("other"))
        assert not Or(Root(), Fields("name")) == And(Root(), Fields("name"))

    def test_node_equals(self):
        assert Root() == Root()
        assert This() == This()
        assert Index(2) == Index(2)
        assert Len() == Len()
        assert Sum() == Sum()
        assert Avg() == Avg()
        assert Sorted() == Sorted()
        assert And(Root(), Fields("name")) == And(Root(), Fields("name"))
        assert Or(Root(), Fields("name")) == Or(Root(), Fields("name"))

        assert Child(Root(), Fields("name")) == Child(Root(), Fields("name"))
        assert Where(Root(), Fields("name")) == Where(Root(), Fields("name"))


class TestRoot(TestCase):
    def setUp(self):
        self._root = Root()
        self._data = {"data": [{"name": "jorge"}, {"name": "james"}]}

    def test_find(self):
        self.assertEqual(list(self._root.find({})), [{}])
        self.assertEqual(list(self._root.find(None)), [None])
        self.assertEqual(list(self._root.find(self._data)), [self._data])
        self.assertEqual(list(self._root.find(34)), [34])
        self.assertEqual(list(self._root.find("")), [""])


class TestChild(TestCase):
    def test_find(self):
        child = Child(Root(), Fields("value"))
        self.assertEqual(find(child, {"value": 23}), [23])
        self.assertEqual(find(child, dict()), [])
        self.assertEqual(find(child, {"other": 23}), [])


class TestWhere(TestCase):
    def test_find(self):
        data = {"data": [{"value": 2}, {"other": 3}]}
        child = Child(Child(Root(), Fields("data")), AllIndex())
        where = Where(child, Fields("value"))
        self.assertEqual(find(where, data), [{"value": 2}])


class TestDescendants(TestCase):
    def test_equal(self):
        assert Descendants(Root(), Fields("name")) == Descendants(
            Root(), Fields("name")
        )


class TestThis(TestCase):
    def setUp(self):
        self._this = This()
        self._data = {"data": [{"name": "jorge"}, {"name": "james"}]}

    def test_find(self):
        self.assertEqual(list(self._this.find(None)), [None])
        self.assertEqual(list(self._this.find({})), [{}])
        self.assertEqual(list(self._this.find(self._data)), [self._data])
        self.assertEqual(list(self._this.find(34)), [34])
        self.assertEqual(list(self._this.find("")), [""])


class TestFields(TestCase):
    def test_find_negative_cases(self):
        extra = ([1, 3, 4], "the word", "")
        assert_with_error(self, Fields("*"), JPathNodeError, extra_cases=extra)

    def test_find_positive_cases(self):
        data = {"data": "value", "is_valid": True, 2: 34, True: False}
        cases = (("data", ["value"]), ("is_valid", [True]), (2, [34]), (True, [False]))
        for key, expected in cases:
            self.assertEqual(Fields(key).find(data), expected)


def assert_with_error(tester, instance, error, extra_cases=tuple()):
    cases = (24, True, 3.4, None)
    for case in cases + extra_cases:
        with tester.assertRaises(error):
            instance.find(case)


class TestSlice(TestCase):
    def test_equal(self):
        assert Slice(2, 6, 3) == Slice(2, 6, 3)
        assert Slice() == Slice()
        assert not Slice(2, 6, 3) == Slice(2, 0, 3)

    def test_find(self):
        data = [1, 2, 3, 4, 5]
        self.assertEqual(find(Slice(step=2), data), [1, 3, 5])
        self.assertEqual(find(Slice(start=0, end=4, step=2), data), [1, 3])
        self.assertEqual(find(Slice(start=-4, end=8, step=4), data), [2])
        self.assertEqual(find(Slice(start=4, end=-4, step=3), data), [])
        self.assertEqual(find(Slice(), {"data": 1}), [{"data": 1}])

    def test_find_in_string(self):
        data = "This is an string"
        self.assertEqual(find(Slice(start=1, end=4), data), ["his"])
        self.assertEqual(find(Slice(start=1, end=6, step=2), data), ["hsi"])
        self.assertEqual(find(Slice(), data), [data])

    def test_find_with_exception(self):
        assert_with_error(self, Slice(), JPathNodeError)


def make_verification(tester, node, datum, expected):
    tester.assertEqual([d for d in node.find(datum)], expected)


def assert_error_in_index(tester, class_, indexes, data, error):
    for index in indexes:
        with tester.assertRaises(error):
            class_(index).find(data)


class TestIndex(TestCase):
    def test_find(self):
        list_ = ["value", 3, False, "true", -5]
        make_verification(self, Index(3), list_, ["true"])
        make_verification(self, Index(0), list_, ["value"])
        make_verification(self, Index(-1), list_, [-5])
        make_verification(self, Index(4), list_, [-5])

    def test_find_index_error(self):
        assert_error_in_index(
            self, Index, (6, -6), ["value", 3, False, -5], JPathIndexError
        )
        assert_error_in_index(self, Index, (6, -6), "Hi", JPathIndexError)

    def test_find_index_error_in_empty_list(self):
        assert_error_in_index(self, Index, (6, -6, 1, 0), [], JPathNodeError)

    def test_find_index_error_in_str(self):
        assert_error_in_index(self, Index, (6, -6, 1, 0), "", JPathNodeError)

    def test_find_exceptions(self):
        cases = (23, True, 23.3, None)
        for case in cases:
            with self.assertRaises(JPathNodeError):
                Index(0).find(case)

    def test_equal(self):
        assert Index(2) == Index(2)
        assert Index(0) == Index(0)
        assert Index(-10) == Index(-10)
        assert not Index(6) == Index(-5)


class TestAllIndex(TestCase):
    def test_find_in_list(self):
        list_ = ["value", 3, False, "true", -5]
        make_verification(self, AllIndex(), list_, list_)
        make_verification(self, AllIndex(), [], [])

    @pytest.mark.skipif(
        sys.version_info < (3, 0), reason="Py2 return the dict values in other order"
    )
    def test_find_in_dict(self):
        dict_ = {"One": 1, 2: "Two", True: None}
        make_verification(self, AllIndex(), dict_, [1, "Two", None])
        make_verification(self, AllIndex(), {}, [])

    def test_find_exceptions(self):
        cases = (23, True, 23.3, None)
        for case in cases:
            with self.assertRaises(JPathIndexError):
                AllIndex().find(case)

    def test_equal(self):
        assert AllIndex() == AllIndex()


class TestLen(TestCase):
    def test_find(self):
        cases = [
            ([False, "true", -5, "value", 3], [5]),
            (dict(), [0]),
            (tuple(), [0]),
            ("example", [7]),
        ]
        for data, expected in cases:
            make_verification(self, Len(), data, expected)

    def test_find_with_exception(self):
        assert_with_error(self, Len(), JPathNodeError)

    def test_equal(self):
        assert Len() == Len()


class TestSorted(TestCase):
    @pytest.mark.skipif(
        sys.version_info < (3, 0), reason="Py str dont have __iter__ attr"
    )
    def test_find(self):
        cases = (
            ([2, 7, 4, 1], [[1, 2, 4, 7]]),
            ("hola", [["a", "h", "l", "o"]]),
            ({"2": "two", "1": "one"}, [["1", "2"]]),
        )
        sorted_ = Sorted()
        for case, expected in cases:
            self.assertEqual(find(sorted_, case), expected)

    def test_find_with_exception(self):
        assert_with_error(self, Sorted(), JPathNodeError)


class TestSum(TestCase):
    def test_find(self):
        cases = [
            ([2, 3, 4, 2, -5], [6]),
            ({1: "one", 2: "two"}, [3]),
            (list(), [0]),
            (dict(), [0]),
            (tuple(), [0]),
        ]
        for data, expected in cases:
            make_verification(self, Sum(), data, expected)

    def test_equal(self):
        assert Sum() == Sum()

    def test_find_with_exception(self):
        extra = (
            {"one": 1, "two": 2},
            ["this", "is", "sparta"],
            ["value", 3, False, "true", -5],
        )
        assert_with_error(self, Sum(), JPathNodeError, extra_cases=extra)


class TestAvg(TestCase):
    def test_find(self):
        cases = [
            ({1: "one", 2: "two"}, [1.5]),
            ([2, 3, 4, 2, -5], [1.2]),
            ([2.5, True, 0.5, 0], [1.0]),
        ]
        for data, expected in cases:
            make_verification(self, Avg(), data, expected)

    def test_equal(self):
        assert Avg() == Avg()

    def test_find_with_exception(self):
        extra = (
            ["this", "is", "sparta"],
            ["value", 3, False, "true", -5],
            {"one": 1, "two": 2},
            list(),
            dict(),
            tuple(),
            [],
        )
        assert_with_error(self, Avg(), JPathNodeError, extra_cases=extra)


class TestFilter(TestCase):
    def test_find_with_none_expressions(self):
        data = {"data": 2}
        data_2 = [{"data": 2}, {"data": 4}]
        self.assertEqual(find(Filter(None), data), [data])
        self.assertEqual(find(Filter([]), data), [data])
        self.assertEqual(find(Filter({}), data), [data])
        expr = Expression(Child(Root(), Fields("data")), "==", 2)
        self.assertEqual(find(Filter(expr), data_2), [{"data": 2}])

    def test_find_with_exception(self):
        expr = Expression(Child(Root(), Fields("data")), "==", 2)
        assert_with_error(self, Filter(expr), JPathNodeError)

    def test_find_with_no_list(self):
        expr = Expression(Child(Root(), Fields("data")), "==", 2)
        self.assertEqual(find(Filter(expr), {}), [])

    def test_find(self):
        data = [{"value": 2}, {"other": 3}, {"value": 1}]
        exp = Expression(Child(This(), Fields("value")), "<=", 2)
        self.assertEqual(find(Filter(exp), data), [{"value": 2}, {"value": 1}])

    @pytest.mark.skipif(
        sys.version_info < (3, 0), reason="string unicode repr diff py2 and 3"
    )
    def test_filter_str_and_repr(self):
        self.assertEqual(str(Filter("")), "[?()]")
        self.assertEqual(str(Filter([])), "[?([])]")
        self.assertEqual(str(Filter(Expression())), "[?()]")

        self.assertEqual(repr(Filter([])), "Filter([])")
        self.assertEqual(
            repr(Filter(Expression())), "Filter(Expression(target='',op='',value=''))"
        )


class TestExpression(TestCase):
    def test_find(self):
        data = {"value": 2, "other": 3}
        self.assertEqual(
            Expression(Child(This(), Fields("value")), "==", 2).find(data), True
        )
        self.assertEqual(
            Expression(Child(This(), Fields("other")), "<", 6).find(data), True
        )
        self.assertEqual(
            Expression(Child(This(), Fields("value")), None, 2).find(data), True
        )
        self.assertEqual(
            Expression(Child(This(), Fields("val")), ">=", 4).find({}), False
        )

    def test_equal(self):
        self.assertEqual(Expression("", "", ""), Expression("", "", ""))
        self.assertEqual(
            Expression(Child(This(), Fields("name")), "==", 4),
            Expression(Child(This(), Fields("name")), "==", 4),
        )
        self.assertNotEqual(Expression("", "", ""), Expression(None, None, None))

    def test_str_and_repr(self):
        self.assertEqual(str(Expression("", "", "")), "")
        self.assertEqual(
            str(Expression(Child(This(), Fields("name")), ">", 10)), "@.name>10"
        )

        self.assertEqual(
            repr(Expression("", "", "")), "Expression(target='',op='',value='')"
        )
        self.assertEqual(
            repr(Expression("name", ">", 10)),
            "Expression(target='name',op='>',value=10)",
        )


class TestRecursive(TestCase):
    def setUp(self):
        self._data = {
            "items": {
                "products": [
                    {"name": "dishes", "price": 12},
                    {"name": "spoon", "price": 32},
                ]
            }
        }

    def test_find_recursive(self):
        self.assertEqual(Recursive.find(self._data, Fields("price")), [12, 32])
        self.assertEqual(
            Recursive.find(self._data, Fields("name")), ["dishes", "spoon"]
        )

    def test_find_in_dict(self):
        result = []
        Recursive.find_in_dict(self._data, Fields("name"), result)
        self.assertEqual(result, ["dishes", "spoon"])

        result = []
        Recursive.find_in_dict(self._data, Fields("other"), result)
        self.assertEqual(result, [])

        result = []
        Recursive.find_in_dict(self._data, Fields("items"), result)
        self.assertEqual(result, [self._data["items"]])

        result = []
        Recursive.find_in_dict({}, Fields("items"), result)
        self.assertEqual(result, [])


class TestOperator(TestCase):
    def test_find_abstract_method_increase_coverage(self):
        self.assertEqual(Operator("l", "r", ">").find({}), None)

    def test_make_op_add(self):
        cases = (
            ("show ", "me", "show me"),
            (2, 4, 6),
            ([2, 3], 2, None),
            ({"a": 2}, 3, None),
            ([2], [3], [2, 3]),
            (True, 2, 3),
            (False, 2, 2),
            (True, True, 2),
            (False, False, 0),
        )
        for left, right, expected in cases:
            self.assertEqual(Operator.make_op(left, right, OPERATOR_MAP["+"]), expected)

    def test_make_op_sub(self):
        cases = (
            (2, 4, -2),
            ("show ", "me", None),
            ([2, 3], 2, None),
            ({"a": 2}, 4, None),
            ([2], [3], None),
            (True, 2, -1),
            (False, 2, -2),
            (True, True, 0),
            (False, False, 0),
        )
        for left, right, expected in cases:
            self.assertEqual(Operator.make_op(left, right, OPERATOR_MAP["-"]), expected)

    def test_make_op_mul(self):
        cases = (
            ("show ", "me", None),
            (2, 4, 8),
            ([2, 3], 2, [2, 3, 2, 3]),
            ({"a": 2}, 4, None),
            ([2], [3], None),
            (True, 2, 2),
            (False, 2, 0),
            (True, True, 1),
            (False, False, 0),
        )
        for left, right, expected in cases:
            self.assertEqual(Operator.make_op(left, right, OPERATOR_MAP["*"]), expected)

    def test_make_op_div(self):
        cases = (
            (8, 4, 2),
            ("show ", "me", None),
            ([2, 3], 2, None),
            ({"a": 2}, 4, None),
            ([2], [3], None),
            (True, 2, 0.5),
            (False, 2, 0),
            (True, True, 1),
            (False, False, None),
        )
        for left, right, expected in cases:
            self.assertEqual(Operator.make_op(left, right, OPERATOR_MAP["/"]), expected)

    def test_make_op_list(self):
        cases = (
            ([8], [4], OPERATOR_MAP["+"], [12]),
            (["show "], ["me"], OPERATOR_MAP["-"], [None]),
            ([[2, 3]], [2], OPERATOR_MAP["*"], [[2, 3, 2, 3]]),
            ([{"a": 2}], [4], OPERATOR_MAP["/"], [None]),
            ([2, 3], [3], OPERATOR_MAP["+"], [5, 6]),
            ([True], [2], OPERATOR_MAP["/"], [0.5]),
            ([False], [2], OPERATOR_MAP["*"], [0]),
            ([True], [True], OPERATOR_MAP["/"], [1]),
            ([False], [False], OPERATOR_MAP["/"], [None]),
        )
        for left, right, op, expected in cases:
            self.assertEqual(Operator.make_op_list(left, right, op), expected)
