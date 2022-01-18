import json
import os

from time import time

from jsonpath_ng.ext import parse as o_parse
from memory_profiler import profile
from jpath_finder.jpath_parser import parse as n_parse


BASIC_PATHS = [
    "$.name",
    "$.data[0].id",
    "$.data[0].type",
    "$.data[0].attributes.title",
    "$.data[0].attributes.body",
    "$.data[0].attributes.created",
    "$.data[0].attributes.updated",
    "$.data[0].attributes.info.meta.totalPages",
    "$.data[0].attributes.info.data_2[*].id",
    "$.data[0].attributes.info.data_2[*].type",
    "$.data[0].attributes.info.data_2[*].attributes.title",
    "$.data[0].attributes.info.data_2[*].attributes.body",
    "$.data[0].attributes.info.data_2[*].attributes.created",
    "$.data[0].attributes.info.data_2[*].attributes.updated",
    "$.data[0].attributes.info.data_2[*].attributes.others.errors[1].status",
    "$.data[0].attributes.info.data_2[*].attributes.others.errors[1].source.pointer",
    "$.data[0].attributes.info.data_2[*].attributes.others.errors[1].detail",
    "$.data[0].attributes.info.links.self",
    "$.data[0].attributes.info.links.first",
    "$.data[0].attributes.info.links.prev",
    "$.data[0].attributes.info.links.next",
    "$.data[0].attributes.info.links.last",
    "$.data[0].attributes.info.other.errors[0].source.parameter",
    "$.data[0].attributes.info.other.errors[0].title",
    "$.data[0].attributes.info.other.errors[0].detail",
    "$.data[0].relationships.author.data.id",
    "$.data[0].relationships.author.data.type",
    "$.included[0].type",
    "$.included[0].id",
    "$.included[0].attributes.name",
    "$.included[0].attributes.age",
    "$.included[0].attributes.gender",
    "$.applications.data[0].type",
    "$.applications.data[0].id",
    "$.applications.data[0].attributes.title",
    "$.applications.data[0].attributes.body",
    "$.applications.data[0].relationships.author.data.id",
    "$.applications.data[0].relationships.author.data.type",
    "$.applications.included[0].type",
    "$.applications.included[0].id",
    "$.applications.included[0].attributes.name",
    "$.list_items[4]",
    "$.data..title",
    "$.data..body",
    "$.data..created",
    "$.data..updated",
    "$.data..totalPages",
    "$.data..id",
    "$.data..type",
    "$.data..status",
    "$.data..pointer",
    "$..name",
]

EXTENDED_PATHS = [
    # "$.list_items[0::3]",
    # "$.list_items[:6:2]",
    # "$.list_items_2[::]",
    "$.data_3.items.products[?(@.name == 'dishes')].price",
    "$.objects_4[?(@.cow > 5 & @.cat == 2)].cow",
    "$.payload.metrics[?(@.id>1)].name",
    "$.payload.metrics[?(@.id==2)].value",
    "$.payload.metrics[?(@.id<=2)].source",
    "$.payload.metrics[?(@.id>5)].name",
    "$.items[?(@.quotas[*].usage>3)].quotas[*].metric",
    "$.items[?(@.quotas[*].usage=0)].quotas[*].usage",
    "$.items[?(@.quotas[*].usage>=0)].quotas[*].limit",
    # "$.items[?(@.quotas[*].usage==3 | @.quotas[*].limit==21)].metric",
    "$.items[?(@.quotas[*].usage==3 & @.quotas[*].limit==21)].quotas[*].usage",
    "$.items[?(@.quotas[*].usage==3 & @.quotas[*].limit==21 & "
    "@.quotas[*].metric=='CPUS')].quotas[*].limit",
    "$.objects_4[?(@.cow==8)].cat",
    "$.objects_4[?(@.cow==8)].cow",
    "$.objects_4[?(@.cow>=3)].cat",
    "$.objects_4[?(@.cat=='Mew')].cat",
    "$.data_5.virtual_machines[?(@.cpu=4 & @.name=='Windows')]",
    "$.data_5.virtual_machines[?(@.cpu=11 & @.ram==2.2)]",
    "$.large_data[?(@.isActive == true)].vms[?(@.cores > 2)]"
    ".countries[?(@.quantity > 30)].country_name",
    "$.large_data[?(@.isActive == true)].vms[?(@.cores >= 1)]"
    ".countries[?(@.country_name == 'Maine')].quantity",
    "$.large_data[?(@.isActive == false)].vms[?(@.cores == 4)]"
    ".countries[?(@.country_name == 'Arizona')].quantity",
]

SOLVE = [
    # "$.large_data[?(@.isActive == true)].vms[?(@.cores > 2)]"
    # ".countries[?(@.quantity > 30)].country_name",
    # "$.large_data[?(@.isActive == true)].vms[?(@.cores >= 1)]"
    # ".countries[?(@.country_name == 'Maine')].quantity",
    "$.large_data[?(@.isActive == true)].vms[*].countries[*].quantity"
    # "$.large_data[?(@.isActive == false)].vms[?(@.cores == 4)]"
    # ".countries[?(@.country_name == 'Arizona')].quantity"
    # "$.name",
    # "$.items[?(@.quotas[*].usage>3)].quotas[*].metric",
    # "$.items[?(@.quotas[*].usage=0)].quotas[*].usage",
    # "$.items[?(@.quotas[*].usage>=0.0)].quotas[*].limit",
    # "$.items[?(@.quotas[*].usage==3 & @.quotas[*].limit==21)].quotas[*].usage",
    # "$.items[?(@.quotas[*].usage==3 & @.quotas[*].limit==21 & @.quotas[*]"
    # ".metric=='CPUS')].quotas[*].limit"
]

DESCENDANTS = [
    "$.list_items[4]",
    "$.data..title",
    "$.data..body",
    "$.data..created",
    "$.data..updated",
    "$.data..totalPages",
    "$.data..id",
    "$.data..type",
    "$.data..status",
    "$.data..pointer",
    "$..name",
]


class JPPerformance(object):
    @staticmethod
    @profile(precision=6)
    def test_performance_n_time_profiled(data, paths, times=1):
        t1, r1, p1 = JPPerformance.parse_paths(n_parse, data, paths, "NEW", times)

        t2, r2, p2 = JPPerformance.parse_paths(o_parse, data, paths, "ORIGINAL", times)

        is_result_equal = JPPerformance.compare_results(r1, r2)
        JPPerformance.print_difference(t1, t2, is_result_equal)

    @staticmethod
    def test_performance_time(data, paths, times=1):
        t1, r1, p1 = JPPerformance.parse_paths(n_parse, data, paths, "NEW", times)

        t2, r2, p2 = JPPerformance.parse_paths(o_parse, data, paths, "ORIGINAL", times)

        is_result_equal = JPPerformance.compare_results(r1, r2)
        JPPerformance.print_difference(t1, t2, is_result_equal)

    @staticmethod
    def parse_paths(parse_method, data, j_paths, label, times=1):
        init = time()
        results = []
        parses = []
        for _ in range(times):
            print("Iteration: {0}".format(_ + 1))
            for j_path in j_paths:
                parsed = parse_method(j_path)
                parses.append(parsed)
                result = parsed.find(data)
                results.append(result)
                # print(result)
                # print(parsed)
        diff = time() - init
        separator = "-" * 20
        summary = """
        {0}{1} JSON PATH{0}
        Time: {2:.4f} seconds
        """
        print(summary.format(separator, label, diff))
        return diff, results, parses

    @staticmethod
    def standardize(result):
        return [m.value if hasattr(m, "value") else m for m in result]

    @staticmethod
    def compare_results(r_1, r_2):
        all_equals = []
        for index, (r1, r2) in enumerate(zip(r_1, r_2)):
            result_1 = JPPerformance.standardize(r1)
            result_2 = JPPerformance.standardize(r2)
            is_equal = result_1 == result_2
            # compare_results = """{0} {1} {2} {3}"""
            # print(compare_results.format(index, is_equal, result_1, result_2))
            if not is_equal:
                print("Not equal", r1, r2, index)
            all_equals.append(is_equal)
        return all(all_equals)

    @staticmethod
    def print_difference(time_1, time_2, result_equal):
        separator = "-" * 20
        summary = """
        {0} Result Time {0}
        New Parser: {1:.3f} seconds
        Original parser: {2:.3f} seconds
        Reduced times TIME_2/TIME_1: {3:.3f}
        The results are the same: {4}
        """
        print(summary.format(separator, time_1, time_2, time_2 / time_1, result_equal))


if __name__ == "__main__":
    # json_for_test.json          555 lines
    # large_json_for_test.json  49653 lines   'large_data:' len 1475

    json_file_name = "json_for_test.json"
    json_paths = BASIC_PATHS  # + EXTENDED_PATHS

    with open(os.path.abspath(json_file_name), "r") as file:
        json_data = json.load(file)

        # measure performance
        # JPPerformance.test_performance_time(json_data, json_paths, times=1)

        # measure resource used
        JPPerformance.test_performance_n_time_profiled(json_data, json_paths, times=1)
