"""Declared topology (network model definition)"""

from __future__ import print_function

import json
import sys

# pylint: disable=import-error
from declared_node import DeclaredTopologyNode

# pylint: disable=import-error
from declared_link import DeclaredTopologyLink


class DeclaredTopology:
    """Topology data wrapper"""

    def __init__(self, json_path):
        self._read_json_file(json_path)

    def _read_json_file(self, json_path):
        try:
            with open(json_path, "r") as file:
                self._dict = json.load(file)
                self._nodes = [DeclaredTopologyNode(node) for node in self._dict["nodes"]]
                self._links = [DeclaredTopologyLink(link) for link in self._dict["links"]]
        # pylint: disable=broad-except
        except Exception as error:
            print("Error: file %s not found or invalid json: %s" % (json_path, error), file=sys.stderr)
            sys.exit(1)

    @property
    def nodes(self):
        """any type of nodes (host, router, switch)"""
        return self._nodes

    def node(self, name):
        """find node by name"""
        return next((node for node in self.nodes if node.name == name), None)

    @property
    def linux_hosts(self):
        """host and router type nodes"""
        return [node for node in self.nodes if node.is_host or node.is_router]

    @property
    def switches(self):
        """switch nodes"""
        return [node for node in self.nodes if node.is_switch]

    @property
    def links(self):
        """links (list of link)"""
        return self._links

    def link_connected_to(self, node_name, intf_name):
        """find link connected to specified node/interface"""
        return next((link for link in self.links if link.connected_to(node_name, intf_name)), None)

    def link_to_interfaces(self, link):
        """
        Args:
            link (DeclaredTopologyLink)
        Returns:
            list(DeclaredTopologyIntf)
        """
        intf1 = self.node(link.tp1.node).intf(link.tp1.intf)
        intf2 = self.node(link.tp2.node).intf(link.tp2.intf)
        return [intf1, intf2]

    def __str__(self):
        return self.to_json_str()

    def to_json_str(self):
        """convert topology data into json string"""
        return json.dumps(self._dict)
