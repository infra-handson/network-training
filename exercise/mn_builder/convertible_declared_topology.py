"""
declared topology (network topology definition) with data convert function (yaml/json)

Notice: this script is for python >=3 ('yaml' added v3) NOT for mininet env construction.
"""

import json
import re
import sys
import yaml

# pylint: disable=import-error
from declared_topology import DeclaredTopology

# pylint: disable=import-error
from declared_node import DeclaredTopologyNode

# pylint: disable=import-error
from declared_link import DeclaredTopologyLink

# pylint: disable=too-many-ancestors
class MyDumper(yaml.Dumper):
    """
    see: python yaml.dump bad indentation - Stack Overflow
    https://stackoverflow.com/questions/25108581/python-yaml-dump-bad-indentation
    """

    def increase_indent(self, flow=False, indentless=False):
        """indentation modifier"""
        # pylint: disable=super-with-arguments
        return super(MyDumper, self).increase_indent(flow, False)


class ConvertibleDeclaredTopology(DeclaredTopology):
    """Topology data with data convert function"""

    def __init__(self, file_path, input_format):
        self._json_regexp = re.compile(r"json")
        self._yaml_regexp = re.compile(r"ya?ml")

        if self._is_json_format(input_format):
            # pylint: disable=super-with-arguments
            super(ConvertibleDeclaredTopology, self).__init__(file_path)
        elif self._is_yaml_format(input_format):
            self._read_yaml_file(file_path)
        else:
            print("  * Error: unknown input file format: %s" % input_format, file=sys.stderr)
            sys.exit(1)

    def _is_json_format(self, format_string):
        return re.search(self._json_regexp, format_string)

    def _is_yaml_format(self, format_string):
        return re.search(self._yaml_regexp, format_string)

    def _read_yaml_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                self._dict = yaml.safe_load(file)
                self._nodes = [DeclaredTopologyNode(node) for node in self._dict["nodes"]]
                self._links = [DeclaredTopologyLink(link) for link in self._dict["links"]]
        # pylint: disable=broad-except
        except Exception as error:
            print("  * Error: file %s not found or invalid yaml: %s" % (file_path, error), file=sys.stderr)
            sys.exit(1)

    def print_dict(self, output_format):
        """print dictionary with specified data format (json/yaml)"""
        if self._is_json_format(output_format):
            self._print_dict_json()
        elif self._is_yaml_format(output_format):
            self._print_dict_yaml()
        else:
            print("  * Error: Unknown output format: %s" % output_format, file=sys.stderr)
            sys.exit(1)

    def _print_dict_json(self):
        print(json.dumps(self._dict, indent=2))

    def _print_dict_yaml(self):
        print(yaml.dump(self._dict, Dumper=MyDumper, default_flow_style=False))
