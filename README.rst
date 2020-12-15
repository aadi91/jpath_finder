Python JSONPath
=====================================================

An implementation of JsonPath for python with a good performance.

About
-----

This library was created based on the https://github.com/h2non/jsonpath-ng library.

The following changes were made in order to improve the execution time and decrease memory usage:

- Refactor all JsonPath classes.
- Refactor datum_in_context class and called Datum.
- Add new functionality like Slice, Sum, Avg, Or, `keys`, `values`.
- The Parser and Lexer were refactored partially and their methods were changed to static methods.
- Remove update and filter methods, this library just implement the find method.
- Add new error classes.


Quick Start
-----------

To install, use pip:

.. code:: bash

    $ pip install jpath-finder


Usage
-----
Basic usage : **find** : method:

.. code:: python

    $ python
    >>> from jpath_finder.jpath_parser import find

    # find("jsonpath", json_data)
    # Easy way to extract values through jsonpath.
    >>> find("foo[*].baz", {"foo": [{"baz": 1}, {"baz": 2}]})
    [1, 2]

    # Also we can use an index '1' from a list or string.
    >>> find("foo[1].baz", {"foo": [{"baz": 1}, {"baz": 2}]})
    [2]

    >>> find("foo[1][1:6]", {"foo": ["The example", "String example"]})
    ['tring']

    >>> find("foo..baz", {"foo": [{"baz": 1}, {"baz": 2}]})
    [1, 2]

    # debug=True if you can log the error.
    # find("jsonpath", json_data, debug=True)
    >>> find("[2]", 123, debug=True)
    JPathNodeError: Invalid Path [2] for 123
    []

    # debug=False by default
    # find("jsonpath", json_data)
    >>> find("[2]", 123)
    []

    # Note: if you have a custom_logger, it needs a debug method like "custom_logger.debug(message)".
    # find("[2]", 123, logger=custom_logger, debug=True)


Basic usage : **find_datum** : method:

Note:
Unlike **find** with **find_datum** we can obtain the path where the result value is found, with:

- datum.value to retrieve the value found.
- str(datum) to get the path of this value.

.. code:: python

    $ python
    >>> from jpath_finder.jpath_parser import find_datum

    # find_datum("jsonpath", json_data)
    >>> find_datum("foo[*].baz", {"foo": [{"baz": 1}, {"taz": 2}]})
    [<jpath_finder.jpath_datum.Datum object at 0x000001BABB06AB00>]

    >>> [(str(d), d.value) for d in find_datum("foo[*].baz", {"foo": [{"baz": 1}, {"baz": 2}]})]
    [('$[foo][0][baz]', 1), ('$[foo][1][baz]', 2)]

    # Also we can use an index '1' from a list or string.
    >>> [(str(d), d.value) for d in find_datum("foo[1].baz", {"foo": [{"baz": 1}, {"baz": 2}]})]
    [('$[foo][1][baz]', 2)]

    >>> [(str(d), d.value) for d in find_datum("foo[1][1:6]", {"foo": ["The example", "String example"]})]
    [('$[foo][1][slice(1, 6, None)]', 'tring')]


    >>> [(str(d), d.value) for d in find_datum("foo..baz", {"foo": [{"baz": 1}, {"baz": 2}]})]
    [('$[foo][0][baz]', 1), ('$[foo][1][baz]', 2)]


JSONPath Syntax
---------------
Note: The method **find_datum** doesn't not support all syntax.

+--------------+-------------+----------------------------------------------+-------+------------+
| name         | Syntax      | Example                                      | find  | find_datum |
+==============+=============+==============================================+=======+============+
| Root         |"$"          | * $.objects                                  | YES   | YES        |
+--------------+-------------+----------------------------------------------+-------+------------+
| This         |"@"          | * $.objects[?(@.name=="foo")]                | YES   | YES        |
+--------------+-------------+----------------------------------------------+-------+------------+
| Descendant   |".."         | * $.objects..price                           | YES   | YES        |
+--------------+-------------+----------------------------------------------+-------+------------+
| Union        |"|"          | * $.objects_1 | $.objects_2                  | YES   |            |
+--------------+-------------+----------------------------------------------+-------+------------+
| Fields       |[0-9a-zA-Z]  | * $.objects.price.value                      | YES   | YES        |
+--------------+-------------+----------------------------------------------+-------+------------+
| Index        |[0-9]        | * $.objects[3].value                         | YES   | YES        |
+--------------+-------------+----------------------------------------------+-------+------------+
| AllIndex     |"[*]"        | * $.objects[*].cost                          | YES   | YES        |
+--------------+-------------+----------------------------------------------+-------+------------+
| Slice        |"[2:6:2]"    | * $.objects[2:20:3].cost                     | YES   | YES        |
+--------------+-------------+----------------------------------------------+-------+------------+
| Sorted       |"`sorted`"   | * $.objects.`sorted`                         | YES   |            |
+--------------+-------------+----------------------------------------------+-------+------------+
| len          |"`len`"      | * $.objects.`len`                            | YES   |            |
+--------------+-------------+----------------------------------------------+-------+------------+
| sum          |"`sum`"      | * $.objects.`sum`                            | YES   |            |
+--------------+-------------+----------------------------------------------+-------+------------+
| avg          |"`avg`"      | * $.objects.`avg`                            | YES   |            |
+--------------+-------------+----------------------------------------------+-------+------------+
| filter       |"[?(expr)]"  | * $.objects[?(@some_field > 5)]              | YES   | YES        |
|              |             | * $.objects[?(some_field = "foobar")]        |       |            |
|              |             | * $.objects[?(some_field != "foobar")]       |       |            |
|              |             | * $.objects[?(some_field>5&other<2|other=3)] |       |            |
+--------------+-------------+----------------------------------------------+-------+------------+
| arithmetic   |"+"          | - $.foo + "_" + $.bar                        | YES   |            |
|              |"*"          | - $.foo * 12                                 |       |            |
|              |             | - $.objects[*].cow + $.objects[*].cat        |       |            |
+--------------+-------------+----------------------------------------------+-------+------------+


Contributors
------------

This package is authored and maintained by:

-  William Alvarez https://github.com/wapwallace


Copyright and License
---------------------

Copyright 2020 - William Alvarez

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

::

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
