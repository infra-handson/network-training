#!/usr/bin/env python3
# NOTICE library path: export PYTHONPATH="$PYTHONPATH:$(pwd)/exercise/mn_builder"

import argparse
import re
import sys

sys.path.append("./exercise/mn_builder")
# noinspection PyPep8
from exercise.mn_builder.testable_declared_topology import TestableDeclaredTopology


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Topology consistency checker")
    help_text = "Training network declaration: if oftype exists, works as format converter"
    parser.add_argument("topology", help=help_text)
    formats = ["json", "yaml", "yml"]
    parser.add_argument("-o", "--oftype", choices=formats, default="", help="Output format type")
    args = parser.parse_args()

    iftype = "json"  # default input file format
    if re.match(r".*\.ya?ml$", args.topology):
        iftype = "yaml"

    topology = TestableDeclaredTopology(args.topology, iftype)

    # works as a data format converter when oftype exists.
    if args.oftype:
        topology.print_dict(args.oftype)
        sys.exit(0)

    # data consistency check if oftype does not exist.
    topology.test_uniqueness("node, interface and link uniqueness")
    topology.test_multiple_referenced_link_tp("irregular link term-point reference")
    topology.test_interface_name("interface name is acceptable as veth name")
    topology.test_unused_node_and_intf("unused interface/node")
    topology.test_existence_of_node_and_intf_in_link("definition existence of node/interface in link")
    topology.test_intf_address_of_link_pair("interface address of link_pair")
    topology.test_interface_trunk_vlans_of_link_pair("trunk-vlan config of link_pair")
    topology.test_next_hop_segment("next_hop is in direct connected segment")
    topology.test_finished()
