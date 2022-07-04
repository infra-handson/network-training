"""
declared topology (network topology definition) with consistency check function

Notice: this script is for python >=3.3 ('ipaddress' added v3.3) NOT for mininet env construction
"""

from collections import Counter
import ipaddress
import sys

# pylint: disable=import-error
from convertible_declared_topology import ConvertibleDeclaredTopology


class TestableDeclaredTopology(ConvertibleDeclaredTopology):
    """add consistency test"""

    @staticmethod
    def _print_message0(key, message):
        print("- %s: %s" % (key, message))

    @staticmethod
    def _print_message1(level, message):
        print("  - %s: %s" % (level, message))

    def _error(self, message):
        self._print_message1("error", message)

    def _info(self, message):
        self._print_message1("info", message)

    def _warning(self, message):
        self._print_message1("warning", message)

    def _title(self, message):
        self._print_message0("test", message)

    def _suspend_test(self, messasge):
        self._print_message0("suspend", messasge)
        sys.exit(1)

    def test_finished(self):
        """test finished message"""
        self._print_message0("test", "finished")

    def test_uniqueness(self, title):
        """uniqueness of object identifier (name)"""
        self._title(title)
        found_duplicated_node = self._test_node_name_uniqueness()
        found_duplicated_intf = self._test_interface_name_uniqueness()
        found_duplicated_link = self._test_link_uniqueness()
        if found_duplicated_node or found_duplicated_intf or found_duplicated_link:
            self._suspend_test("fix duplicated node/interface/link at first.")

    def _test_link_uniqueness(self):
        """
        Case:
          [tp1] ========== [tp2]
        """
        found_duplication_link = False
        for link in self.links:
            duplicated_links = [other_link for other_link in self.links if link == other_link]
            if len(duplicated_links) > 1:
                self._error("link %s is not unique" % link)
                found_duplication_link = True
        return found_duplication_link

    def test_multiple_referenced_link_tp(self, title):
        """
        find a term point that connected with multiple-link
        Case:
          [tp1] -----------[tp2]
          [tp3] ----------/
        """
        self._title(title)
        found_multiple_referenced_tp = False
        tps_list = [[link.tp1, link.tp2] for link in self.links]
        tps = sum(tps_list, [])  # flatten
        for term_point in tps:
            multiple_referenced_tps = [other_tp for other_tp in tps if term_point == other_tp]
            if len(multiple_referenced_tps) > 1:
                # pylint: disable=consider-using-set-comprehension
                tps_str_list = list(set(["%s" % intf for intf in multiple_referenced_tps]))  # unique
                self._error("there are multiple link-referenced term points %s" % tps_str_list)
                found_multiple_referenced_tp = True
        return found_multiple_referenced_tp

    def _test_node_name_uniqueness(self):
        found_duplicated_node = False
        node_names = [node.name for node in self.nodes]
        node_name_count = Counter(node_names)
        for node, count in node_name_count.items():
            if count > 1:
                self._error("node %s is not unique" % node)
                found_duplicated_node = True
        return found_duplicated_node

    def _test_interface_name_uniqueness(self):
        found_duplicated_intf = False
        interfaces = sum([node.interfaces for node in self.nodes], [])  # flatten
        interface_names = [intf.name for intf in interfaces]
        interface_names_count = Counter(interface_names)
        for intf, count in interface_names_count.items():
            if count > 1:
                node_names = [node.name for node in self.nodes if node.has_intf(intf)]
                self._error("interface %s in node %s is not unique" % (intf, node_names))
                found_duplicated_intf = True
        return found_duplicated_intf

    def test_interface_name(self, title):
        """interface name fullfill veth name constraints"""
        self._title(title)
        found_invalid_name = False
        for node in self.nodes:
            for intf in node.interfaces:
                found_invalid_name = self._test_interface_format(node, intf)
        if found_invalid_name:
            self._suspend_test("fix invalid interface name at first.")

    def _test_interface_format(self, node, intf):
        found_invalid_name = False
        if not intf.is_valid_veth_name:
            self._error("interface name %s in node %s is invalid as veth" % (intf.name, node.name))
            found_invalid_name = True
        if intf.has_sub_interfaces:
            for sub_intf in intf.sub_interfaces:
                found_invalid_name = self._test_sub_interface_format(node, intf, sub_intf)
        return found_invalid_name

    def _test_sub_interface_format(self, node, intf, sub_intf):
        found_invalid_name = False
        if not sub_intf.is_valid_veth_name:
            self._error(
                "sub-interface name %s of interface %s in node %s is invalid as veth"
                % (sub_intf.name, intf.name, node.name)
            )
            found_invalid_name = True
        return found_invalid_name

    def test_unused_node_and_intf(self, title):
        """find unused node/interface"""
        self._title(title)
        nodes_in_links = list(set(sum([[link.tp1.node, link.tp2.node] for link in self.links], [])))  # flatten-unique
        for node in self.nodes:
            if node.name not in nodes_in_links:
                self._warning("node %s is standalone" % node.name)
                continue

            for intf in node.interfaces:
                if not self.link_connected_to(node.name, intf.name):
                    self._warning("interface %s in node %s is standalone" % (intf.name, node.name))

    def test_existence_of_node_and_intf_in_link(self, title):
        """find all link termination point (node/interface) are defined"""
        self._title(title)
        exist_all_intfs = True
        for link in self.links:
            test1 = self._test_existence_of_node_and_intf(link.tp1)
            test2 = self._test_existence_of_node_and_intf(link.tp2)
            exist_all_intfs = exist_all_intfs and test1 and test2
        if not exist_all_intfs:
            self._suspend_test("fix name correlation at first.")

    def test_intf_address_of_link_pair(self, title):
        """test interface address is same-subnet in each term-point of a link"""
        self._title(title)
        for link in self.links:
            self._test_link_pair_intf_address(link)

    def test_next_hop_segment(self, title):
        """text next-hop address of a route is a menber of directly connected subnet"""
        self._title(title)
        for node in self.nodes:
            l3_interfaces = [intf for intf in node.interfaces if intf.is_l3]
            l3_interfaces.extend(node.sub_interfaces)
            # convert ip address string to `ipaddress` object to calculate subnet calculation
            node_ipaddrs = [ipaddress.ip_interface(intf.ip_addr) for intf in l3_interfaces]
            for route in node.routes:
                self._test_next_hop_is_connected(node.name, node_ipaddrs, route)

    def _test_next_hop_is_connected(self, node_name, node_ipaddrs, route):
        """
        Args:
            node_name (str): node name
            node_ipaddrs (list(IPv4Interface)): list of ip address owned a node
        """
        try:
            if route.next_hop.lower() == "blackhole":
                self._info("next-hop for %s is blackhole" % route.dst_net)
                return

            next_hop_ip = ipaddress.ip_interface(route.next_hop)
            self._next_hop_is_not_connected(node_name, node_ipaddrs, route, next_hop_ip)
            self._next_hop_is_at_self(node_name, node_ipaddrs, route, next_hop_ip)
            self._next_hop_is_network_addr(node_name, node_ipaddrs, route, next_hop_ip)
            self._next_hop_is_broadcast_addr(node_name, node_ipaddrs, route, next_hop_ip)
        except ValueError as error:
            self._error("value error in node %s or route %s: %s" % (node_name, route, error))

    def _next_hop_is_not_connected(self, node_name, node_ipaddrs, route, next_hop_ip):
        results = [ip.network.supernet_of(next_hop_ip.network) for ip in node_ipaddrs]
        if True not in results:
            self._error("in node %s, next hop of %s is not connected" % (node_name, route))

    def _next_hop_is_at_self(self, node_name, node_ipaddrs, route, next_hop_ip):
        results = [ip.ip == next_hop_ip.ip for ip in node_ipaddrs]
        if True in results:
            self._error("in node %s, next hop of %s is at self node" % (node_name, route))

    def _next_hop_is_network_addr(self, node_name, node_ipaddrs, route, next_hop_ip):
        results = [ip.network.network_address for ip in node_ipaddrs]
        if next_hop_ip.ip in results:
            self._error("in node %s, next hop of %s is same as network address" % (node_name, route))

    def _next_hop_is_broadcast_addr(self, node_name, node_ipaddrs, route, next_hop_ip):
        results = [ip.network.broadcast_address for ip in node_ipaddrs]
        if next_hop_ip.ip in results:
            self._error("in node %s, next hop of %s is same as broadcast address" % (node_name, route))

    def _test_link_pair_intf_address(self, link):
        """
        Args:
            link (DeclaredTopologyLink): link
        """
        intf1, intf2 = self.link_to_interfaces(link)
        if intf1.is_l2 or intf2.is_l2:
            self._info("Ignore %s (one of term-point is L2)" % link)
            return

        try:
            if intf1.ip_addr == intf2.ip_addr:
                self._error("address duplication in %s" % link)
            if ipaddress.ip_interface(intf1.ip_addr).network != ipaddress.ip_interface(intf2.ip_addr).network:
                self._error("network mismatch in %s" % link)
        except ValueError as error:
            self._error("value error in %s: %s" % (link, error))

    def _test_existence_of_node_and_intf(self, intf_ref):
        """
        Args:
            intf_ref (DeclaredTopologyIntfRef): link termination point (interface-ref)
        """
        node = self.node(intf_ref.node)
        if not node:
            self._error("node %s not found" % intf_ref.node)
            return False

        intf = node.intf(intf_ref.intf)
        if not intf:
            self._error("intf %s not found in node %s" % (intf_ref.intf, intf_ref.node))
            return False

        return True

    def test_interface_trunk_vlans_of_link_pair(self, title):
        """list of vlan is same in each term-point of a link"""
        self._title(title)
        for link in self.links:
            intf1, intf2 = self.link_to_interfaces(link)
            if intf1.assumed_trunk_port and intf2.assumed_trunk_port and intf1.any_trunk_vlans != intf2.any_trunk_vlans:
                self._warning(
                    "vlan trunk mismatch: %s(vlans:%s) <=> %s(vlans:%s)"
                    % (intf1, intf1.any_trunk_vlans, intf2, intf2.any_trunk_vlans)
                )
            else:
                self._info("ignore %s (one of term-point is l3 or l2-access" % link)
