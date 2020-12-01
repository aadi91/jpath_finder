from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
)

import logging
import operator

from abc import abstractmethod

from jpath_finder.jpath_errors import JPathIndexError, JPathNodeError


logger = logging.getLogger(__name__)

OPERATOR_MAP = {
    "!=": operator.ne,
    "==": operator.eq,
    "=": operator.eq,
    "<=": operator.le,
    "<": operator.lt,
    ">=": operator.ge,
    ">": operator.gt,
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}


class CBE(object):
    """
    Callback executor this class execute its callbacks.
    """

    @staticmethod
    def execute(callback, exception, *args):
        try:
            return callback(*args)
        except Exception:
            raise exception

    @staticmethod
    def get_index(*args):
        index, data = args
        return data[index]

    @staticmethod
    def get_all(*args):
        index, data = args
        return list(data)[index]

    @staticmethod
    def get_sliced(*args):
        index, data = args
        return data[index]

    @staticmethod
    def get_multiple_index(indexes, data):
        res = []
        for index in indexes:
            try:
                res.append(CBE.get_index(index, data))
            except Exception:
                pass
        return res

    @staticmethod
    def get_attr(*args):
        attr, data = args
        return getattr(data, attr)()

    @staticmethod
    def cb_filter(*args):
        lambda_, data = args
        return list(filter(lambda_, data))

    @staticmethod
    def cb_avg(data):
        return sum(data) / len(data)


class ASTBase(object):
    STR = ""
    REPR = ""

    def __str__(self):
        return self.STR.format(**vars(self))

    def __repr__(self):
        return self.REPR.format(**vars(self))

    @staticmethod
    def none_to_empty(s):
        return "" if s is None else s

    @staticmethod
    @abstractmethod
    def find(data):
        """Abstract method for all AST classes."""
        pass

    def __eq__(self, o):
        return isinstance(o, type(self))


class Leaf(ASTBase):
    """The Leaf base class in the AST."""
    D_MOD = "__mod__"


class Node(ASTBase):
    """The Node base class in the AST"""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __eq__(self, o):
        return ASTBase.__eq__(self, o) and self.left == o.left and self.right == o.right


class Root(Leaf):
    """The Node referring to the "root" or "$" object."""

    STR = "$"
    REPR = "Root()"

    @staticmethod
    def find(data):
        return [data]


class This(Root):
    """The Node referring to the current object or "@"."""

    STR = "@"
    REPR = "This()"


class Child(Node):
    """Node that first matches the left, then the right. Syntax <left> '.' <right>"""

    STR = "{left}.{right}"
    REPR = "Child({left!r}, {right!r})"

    def find(self, data):
        return [v for d in self.left.find(data) for v in self.right.find(d)]


class Where(Child):
    """Node that compare all left values with the right and return it if match."""

    STR = "{left} where {right}"
    REPR = "Where({left!r}, {right!r})"

    def find(self, data):
        return [match for match in self.left.find(data) if self.right.find(match)]


class Descendants(Child):
    """Node that return all matches with the right part. Syntax <left>..<right>."""

    STR = "{left}..{right}"
    REPR = "Descendants({left!r}, {right!r})"

    def find(self, data):
        return [v for m in self.left.find(data) for v in Recursive.find(m, self.right)]


class Union(Child):
    """Node that returns the union of the results of each match."""

    STR = "{left}|{right}"
    REPR = "Union({left!r}|{right!r})"

    def find(self, data):
        return self.left.find(data) + self.right.find(data)


class Fields(Leaf):
    """Node that refers to one or more fields of the current object."""

    STR = "{0}"
    REPR = "Fields({0})"

    def __init__(self, *fields):
        self.fields = fields

    def find(self, value):
        return CBE.get_multiple_index(self.fields, value)

    def __str__(self):
        return self.STR.format(",".join(map(str, self.fields)))

    def __repr__(self):
        return self.REPR.format(",".join(map(repr, self.fields)))

    def __eq__(self, o):
        return isinstance(o, Fields) and tuple(self.fields) == tuple(o.fields)


class Index(Leaf):
    """Node that returns the value of the index on the object."""

    STR = "[{index}]"
    REPR = "Index({index!r})"

    def __init__(self, index):
        self.index = index

    def find(self, data):
        return [CBE.execute(CBE.get_index, JPathIndexError(self, data), self.index, data)]

    def __eq__(self, o):
        return isinstance(o, Index) and self.index == o.index


class AllIndex(Leaf):
    """Node that returns all values of the object."""

    STR = "[*]"
    REPR = "AllIndex()"

    def find(self, data):
        return CBE.execute(CBE.get_all, JPathIndexError(self, data), slice(None, None, None), data)


class Len(Leaf):
    """Node that return the len of the object. Syntax '`len`'"""

    STR = "`len`"
    REPR = "Len()"

    def find(self, data):
        return [CBE.execute(len, JPathNodeError(self, data), data)]


class Sorted(Leaf):
    """Node that return the the object sorted. Syntax '`sorted`'"""

    STR = "`sorted`"
    REPR = "Sorted()"

    def find(self, data):
        return [CBE.execute(sorted, JPathNodeError(self, data), data)]


class Sum(Leaf):
    """Node that return the sum of the object. Syntax '`sum`'"""

    STR = "`sum`"
    REPR = "Sum()"

    def find(self, data):
        return [CBE.execute(sum, JPathNodeError(self, data), data)]


class Avg(Leaf):
    """Node that return the avg of the object. Syntax '`avg`'"""

    STR = "`avg`"
    REPR = "Avg()"

    def find(self, data):
        return [CBE.execute(CBE.cb_avg, JPathNodeError(self, data), data)]


class Keys(Leaf):
    """Node that return the keys of the object. Syntax '`keys`'"""

    STR = "`keys`"
    REPR = "Keys()"
    NAME = "keys"

    def find(self, data):
        return CBE.execute(CBE.get_attr, JPathNodeError(self, data), self.NAME, data)


class Values(Keys):
    """Node that return the values of the object. Syntax '`values`'"""

    STR = "`values`"
    REPR = "Values()"
    NAME = "values"


class Slice(Leaf):
    """Node that make a slice in the object."""

    STR = "[{0}:{1}:{2}]"
    REPR = "Slice(start={0!r},end={1!r},step={2!r})"

    def __init__(self, start=None, end=None, step=None):
        self.start = start
        self.end = end
        self.step = step

    def find(self, data):
        res = CBE.execute(CBE.get_sliced, JPathNodeError(self, data), slice(self.start, self.end, self.step), data)
        return [res] if hasattr(res, self.D_MOD) else res

    def __eq__(self, o):
        return all(
            [
                isinstance(o, Slice),
                self.start == o.start,
                self.end == o.end,
                self.step == o.step,
            ]
        )

    def __str__(self):
        return self.STR.format(
            self.none_to_empty(self.start),
            self.none_to_empty(self.end),
            self.none_to_empty(self.step),
        )

    def __repr__(self):
        return self.REPR.format(
            self.none_to_empty(self.start),
            self.none_to_empty(self.end),
            self.none_to_empty(self.step),
        )


class Filter(Leaf):
    """Node that returns the matches with the filter expressions"""

    STR = "[?({expr})]"
    REPR = "Filter({expr!r})"

    def __init__(self, expression):
        self.expr = expression

    def find(self, data):
        if not self.expr:
            return [data]
        return CBE.execute(CBE.cb_filter, JPathNodeError(self, data), lambda v: self.expr.find(v), data)


class And(Node):
    """Node that returns "True" if <left> and <right> are True"""

    STR = "{left}&{right}"
    REPR = "And({left!r},{right!r})"

    def find(self, datum):
        return self.left.find(datum) and self.right.find(datum)


class Or(Node):
    """Node that returns "True" if <left> or <right> are True"""

    STR = "{left}|{right}"
    REPR = "Or({left!r},{right!r})"

    def find(self, datum):
        return self.left.find(datum) or self.right.find(datum)


class Expression(Leaf):
    """Node expression."""

    STR = "{0}{1}{2}"
    REPR = "{0}(target={1!r},op={2!r},value={3!r})"
    VALUE = "value"

    def __init__(self, target=None, op=None, value=None):
        self.target = target
        self.op = op
        self.value = value

    def find(self, data):
        op = OPERATOR_MAP.get(self.op)
        if hasattr(data, self.VALUE):
            data = data.value
        found = self.target.find(data)
        if op is None:
            return True if found else False
        return any([op(v, self.value) for v in found])

    def __eq__(self, o):
        return all(
            [
                isinstance(o, Expression),
                self.target == o.target,
                self.op == o.op,
                self.value == o.value,
            ]
        )

    def __str__(self):
        return self.STR.format(
            self.none_to_empty(self.target),
            self.none_to_empty(self.op),
            self.none_to_empty(self.value),
        )

    def __repr__(self):
        return self.REPR.format(
            self.__class__.__name__,
            self.none_to_empty(self.target),
            self.none_to_empty(self.op),
            self.none_to_empty(self.value),
        )


class Recursive(object):
    @staticmethod
    def find(data, field):
        result = []
        Recursive.find_recursive(data, field, result)
        return result

    @staticmethod
    def find_recursive(data, field, result):
        if isinstance(data, dict):
            Recursive.find_in_dict(data, field, result)
        elif isinstance(data, list):
            Recursive.find_in_list(data, field, result)

    @staticmethod
    def find_in_dict(data, field, result):
        match = field.find(data)
        if match:
            result.extend(match)
        for value in data.values():
            Recursive.find_recursive(value, field, result)

    @staticmethod
    def find_in_list(data, field, result):
        for value in list(data):
            Recursive.find_recursive(value, field, result)


class Operator(Node):
    STR = "{left}{op_str}{right}"
    REPR = "Operator({left!r},{right!r},{op_str})"

    def __init__(self, left, right, op):
        Node.__init__(self, left, right)
        self.op = OPERATOR_MAP[op]
        self.op_str = op

    @staticmethod
    def make_op(left, right, op):
        try:
            return op(left, right)
        except (TypeError, ZeroDivisionError) as e:
            print(e)
        return None

    @staticmethod
    def make_op_list(left, right, op):
        if len(left) == len(right):
            return [Operator.make_op(le, r, op) for le, r in zip(left, right)]
        return [Operator.make_op(le, r, op) for le in left for r in right]

    @abstractmethod
    def find(self, value):
        pass


class ObjOPObj(Operator):
    def find(self, value):
        return [self.make_op(self.left, self.right, self.op)]


class JPathOPObj(Operator):
    def find(self, value):
        return [self.make_op(v, self.right, self.op) for v in self.left.find(value)]


class JPathOPJPath(Operator):
    def find(self, value):
        return self.make_op_list(self.left.find(value), self.right.find(value), self.op)


class NodesFactory(object):
    @staticmethod
    def mat_operator(left, right, op):
        l_jp = issubclass(left.__class__, Node)
        r_jp = issubclass(right.__class__, Node)
        if l_jp and r_jp:
            return JPathOPJPath(left, right, op)
        elif l_jp:
            return JPathOPObj(left, right, op)
        elif r_jp:
            return JPathOPObj(right, left, op)
        return ObjOPObj(left, right, op)


BINARY_OP_MAP = {"..": Descendants, "where": Where, "|": Union}

NAMED_OPERATOR_MAP = {"sum": Sum, "avg": Avg, "len": Len, "sorted": Sorted, "keys": Keys, "values": Values}

BOOLEAN_OPERATOR_MAP = {"|": Or, "&": And}

ROOT_MAP = {"$": Root, "@": This}
