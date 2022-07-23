"""whole network constructor"""

from __future__ import print_function

import re

# pylint: disable=import-error
from mininet.net import Mininet

# pylint: disable=import-error
from mininet.log import setLogLevel

# pylint: disable=import-error
from mininet.cli import CLI

# pylint: disable=import-error
from mn_node import NetworkTopology


class NetworkConstructor:
    """network constructor"""

    def __init__(self, topology, loglevel):
        """
        Args:
          topology (DeclaredTopology): wrapped topology data
        """
        setLogLevel(loglevel)

        self._topology = topology
        # init mininet topology
        mn_topo = NetworkTopology(self._topology)
        self.net = Mininet(topo=mn_topo, controller=None)

    def run(self):
        """run network with mininet"""
        print("# Run network")
        self.net.start()
        # configure mininet nodes according to declared-topology
        self._config_links_down_in_network()
        self._config_hosts_in_network()  # NOTICE: type:host/router
        self._config_switches_in_network()  # NOTICE: type:switch
        # start CLI
        CLI(self.net)
        # exit
        self.net.stop()

    def _config_links_down_in_network(self):
        for link in self._topology.links:
            if link.is_down_in_initial:
                self._find_tp_and_down(link.tp1)
                self._find_tp_and_down(link.tp2)

    def _find_tp_and_down(self, term_point):
        mn_node = self._find_mn_host_by_name(term_point.node) or self._find_mn_switch_by_name(term_point.node)
        mn_node.down_interface(term_point.intf)

    def _config_switches_in_network(self):
        for switch in self._topology.switches:
            mn_switch = self._find_mn_switch_by_name(switch.name)
            if switch.stp:
                mn_switch.add_bridge_priority_config(switch.stp_priority)
            self._config_mn_switch_interface(mn_switch, switch)

    @staticmethod
    def _config_mn_switch_interface(mn_switch, switch):
        """
        Args:
          mn_switch (ExtendedOVSBridge): switch to configure
          switch (DeclaredTopologyNode): switch info
        """
        for intf in switch.interfaces:
            print("# %s%s" % (mn_switch.name, intf))
            # sub-interfaces are ignored for interfaces in a switch
            if intf.has_l2_access_vlan_config:
                mn_switch.add_l2_access_vlan_config(intf.name, intf.access_vlan)
            elif intf.has_l2_trunk_vlans_config:
                mn_switch.add_l2_trunk_vlans_config(intf.name, intf.trunk_vlans_str)
            else:
                pass  # accept type-l2 and no vlan config (default bridge)

    def _find_mn_switch_by_name(self, name):
        return next((sw for sw in self.net.switches if sw.name == name), None)

    def _config_hosts_in_network(self):
        for node in self._topology.linux_hosts:
            mn_host = self._find_mn_host_by_name(node.name)
            self._config_mn_host_interface(mn_host, node)
            self._config_mn_host_routes(mn_host, node)
            for proc in node.svc_procs:
                print("# %s exec %s" % (mn_host.name, proc))
                mn_host.cmd(proc)

    def _find_mn_host_by_name(self, name):
        return next((host for host in self.net.hosts if host.name == name), None)

    def _config_mn_host_interface(self, mn_host, node):
        """
        Args:
          mn_host (LinuxHost): mininet host to configure
          node (DeclaredTopologyNode): node (host) info
        """
        for intf in node.interfaces:
            print("# %s%s" % (mn_host.name, intf))
            mn_intf = mn_host.intf(intf.name)
            if intf.use_fixed_mac_addr:
                mn_intf.setMAC(intf.mac_addr)
            if intf.is_l3:
                mn_intf.setIP(intf.ip_addr)
            if intf.is_l2:
                mn_host.delete_intf_ip(mn_intf, mn_intf.ip, mn_intf.prefixLen)
            if intf.has_sub_interfaces:
                self._config_mn_host_sub_interface(mn_host, intf.sub_interfaces)

    @staticmethod
    def _config_mn_host_sub_interface(mn_host, sub_interfaces):
        """
        Args:
          mn_host (LinuxHost): mininet host to configure
          sub_interfaces (List<DeclaredSubInterface>): List of sub-interface info
        """
        for sub_intf in sub_interfaces:
            mn_host.add_sub_interface(sub_intf)

    @staticmethod
    def _config_mn_host_routes(mn_host, node):
        """
        Args:
          mn_host (LinuxHost): mininet to configure
          node (DeclaredTopologyNode): node info
        """
        for route in node.routes:
            print("# %s %s" % (mn_host.name, route))
            ret = mn_host.add_route(route.dst_net, route.next_hop)
            if not re.match(r"^\s*$", ret):
                print(ret)  # for debug
