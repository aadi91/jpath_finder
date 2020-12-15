import timeit


PARSE_T = 'parse("{0}")'
FIND_T = 'find("{0}", json_data)'
N_TIMES = 100
IMPORT_PARSE = "from jpath_finder.jpath_parser import parse"
IMPORT_FIND = """
import os
import json
from jpath_finder.jpath_parser import find

json_file_name = "tests/json_for_test.json"
with open(os.path.abspath(json_file_name), "r") as file:
    json_data = json.load(file)
"""


PARSE_PATHS = [
    ("data[0].attributes.info.data_2[*].attributes.title", 0.025, 0.040),
    ("$.items[?(@.quotas[*].usage==3 & @.quotas[*].limit==21)].quotas[*].usage", 0.055, 0.080),
    ("$.data[0].attributes.info.data_2[*].attributes.others.errors[1].source.pointer", 0.045, 0.060),
    ("$.data[0].attributes.info.links.last", 0.020, 0.030),
    ("$.data[0].attributes.info.other.errors[0].source.parameter", 0.035, 0.045),
    ("$.data..title", 0.010, 0.020),
    ("$.list_items[0::3]", 0.010, 0.020),
    ("$.data_3.items.products[?(@.name == 'dishes')].price", 0.030, 0.050),
    ("$.items[?(@.quotas[*].usage==3 & @.quotas[*].limit==21)].quotas[*].usage", 0.050, 0.070),
    ("$.objects_4[?(@.cow==8)].cat", 0.020, 0.040),
    ("$.data_5.virtual_machines[?(@.cpu=4 & @.name=='Windows')]", 0.030, 0.050),
    ("$.large_data[?(@.isActive == true)].vms[?(@.cores >= 1)]", 0.040, 0.050),
    ("$.large_data[?(@.isActive == false)].vms[?(@.cores == 4)]"
     ".countries[?(@.country_name == 'Arizona')].quantity", 0.060, 0.090),
]


def test_parse_performance_by_path():
    for path, t_min, t_max in PARSE_PATHS:
        assert t_min < timeit.timeit(PARSE_T.format(path), number=N_TIMES, setup=IMPORT_PARSE) < t_max


FIND_PATHS = [
    ("data[0].attributes.info.data_2[*].attributes.title", 0.030, 0.050),
    ("$.items[?(@.quotas[*].usage==3 & @.quotas[*].limit==21)].quotas[*].usage", 0.070, 0.150),
    ("$.data[0].attributes.info.data_2[*].attributes.others.errors[1].source.pointer", 0.060, 0.090),
    ("$.data[0].attributes.info.links.last", 0.030, 0.040),
    ("$.data[0].attributes.info.other.errors[0].source.parameter", 0.035, 0.060),
    ("$.data..title", 0.010, 0.040),
    ("$.list_items[0::3]", 0.010, 0.040),
    ("$.data_3.items.products[?(@.name == 'dishes')].price", 0.030, 0.060),
    ("$.items[?(@.quotas[*].usage==3 & @.quotas[*].limit==21)].quotas[*].usage", 0.050, 0.120),
    ("$.objects_4[?(@.cow==8)].cat", 0.020, 0.040),
    ("$.data_5.virtual_machines[?(@.cpu=4 & @.name=='Windows')]", 0.030, 0.060),
    ("$.large_data[?(@.isActive == true)].vms[?(@.cores >= 1)]", 0.040, 0.060),
    ("$.large_data[?(@.isActive == false)].vms[?(@.cores == 4)]"
     ".countries[?(@.country_name == 'Arizona')].quantity", 0.060, 0.110),
]


def test_find_performance_by_path():
    for path, t_min, t_max in FIND_PATHS:
        assert t_min < timeit.timeit(FIND_T.format(path), number=N_TIMES, setup=IMPORT_FIND) < t_max
