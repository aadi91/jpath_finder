from unittest import TestCase

# import jpath_finder.jpath_errors as errors
from jpath_finder.jpath_datum import BaseDatum  # , execute


# def test_execute():
#     assert execute("show me", lambda x: x[0], errors.JPathIndexError("ab", "cd")) == "s"


class TestBaseDatum(TestCase):
    def test_get_attr(self):
        cases = [int(), bool(), str(), float(), list(), dict(), tuple()]
        attrs = ["__len__", "__iter__", "__getitem__", "__mod__", "keys"]
        for case in cases:
            datum = BaseDatum(case)
            for attr in attrs:
                self.assertEqual(hasattr(datum, attr), hasattr(case, attr))
