"""mininet node class"""

from __future__ import print_function

import sys

# pylint: disable=import-error
from mininet.node import Node, OVSBridge

# pylint: disable=import-error
from mininet.topo import Topo


class ExtendedOVSBridge(OVSBridge):
    """Extended OVS Bridge"""

    def add_bridge_priority_config(self, priority):
        """add bridge priority configuration into OVS bridge"""
        opt_str = "set Bridge %s other_config:stp-priority=%s" % (self.name, priority)
        return self.vsctl(opt_str)

    def add_l2_access_vlan_config(self, intf_name, vlan_id):
        """add L2 access port config"""
        opt_str = "set Port %s vlan_mode=access tag=%d" % (intf_name, vlan_id)
        return self.vsctl(opt_str)

    def add_l2_trunk_vlans_config(self, intf_name, vlan_ids_str):
        """add L2 trunk port config"""
        opt_str = "set Port %s vlan_mode=trunk trunks=%s" % (intf_name, vlan_ids_str)
        return self.vsctl(opt_str)

    def down_interface(self, intf_name):
        """change interface state to down"""
        self.cmd("ip link set %s down" % intf_name)


class LinuxHost(Node):
    """Extended Node"""

    # pylint: disable=arguments-differ
    def config(self, **params):
        """configure node settings"""
        # pylint: disable=super-with-arguments
        super(LinuxHost, self).config(**params)
        self.cmd("mkdir -p /var/run/netns")
        # add network namespace link to allow access namespace from external of mininet-CLI
        self.cmd("ln -s /proc/%d/ns/net /var/run/netns/%s" % (self.pid, self.name))

    def terminate(self):
        """terminate node"""
        # clear network namespace link
        self.cmd("rm /var/run/netns/%s" % self.name)
        # pylint: disable=super-with-arguments
        super(LinuxHost, self).terminate()

    def add_route(self, dst_network, next_hop):
        """
        Add static route.
        Args:
            dst_network: default, a.b.c.d/nn
            next_hop: blackhole, e.f.g.h
        """
        if dst_network.lower() == "default":
            self.cmd("ip route del default")

        if next_hop.lower() != "blackhole":
            return self.cmd("ip route add %s via %s" % (dst_network, next_hop))

        return self.cmd("ip route add blackhole %s" % dst_network)

    def delete_intf_ip(self, intf_name, ip_addr, prefix_length):
        """delete interface ip addr (to be L2 mode)"""
        return self.cmd("ip addr del %s/%s dev %s" % (ip_addr, prefix_length, intf_name))

    def add_sub_interface(self, sub_intf):
        """
        add sub interface
        Args:
            sub_intf: {parent_intf_name, name, vlan}
        """
        self.cmd(
            "ip link add link %s name %s type vlan protocol 802.1Q id %d"
            % (sub_intf.parent_intf_name, sub_intf.name, sub_intf.vlan)
        )
        if sub_intf.use_fixed_mac_addr:
            self.cmd("ip link set dev %s address %s" % (sub_intf.name, sub_intf.mac_addr))
        self.cmd("ip addr add %s dev %s" % (sub_intf.ip_addr, sub_intf.name))
        self.cmd("ip link set %s up" % sub_intf.name)

    def down_interface(self, intf_name):
        """Change interface state to down"""
        print("## DEBUG: down interface %s in node %s" % (intf_name, self.name))
        self.cmd("ip link set %s down" % intf_name)

    def __str__(self):
        return self.name


class LinuxRouter(LinuxHost):
    """A Node with IP forwarding enabled."""

    # pylint: disable=arguments-differ
    def config(self, **params):
        """configure node settings"""
        # pylint: disable=super-with-arguments
        super(LinuxRouter, self).config(**params)
        # Enable forwarding on the router
        self.cmd("sysctl net.ipv4.ip_forward=1")

    def terminate(self):
        """terminate node"""
        self.cmd("sysctl net.ipv4.ip_forward=0")
        # pylint: disable=super-with-arguments
        super(LinuxRouter, self).terminate()


class NetworkTopology(Topo):
    """Mininet network topology class"""

    def __init__(self, topology):
        """
        Args:
          topology (DeclaredTopology): wrapped topology data
        """
        self._topology = topology
        # pylint: disable=super-with-arguments
        super(NetworkTopology, self).__init__()

    # Builds network topology
    def build(self, **_opts):
        """build network topology"""
        print("# build topology")
        self._build_nodes()
        self._build_links()

    def _build_nodes(self):
        for index, node in enumerate(self._topology.nodes):
            if node.is_router:
                print("# add node %s as router" % node.name)
                self.addHost(node.name, cls=LinuxRouter)
            elif node.is_host:
                print("# add node %s as host" % node.name)
                self.addHost(node.name, cls=LinuxHost)
            elif node.is_switch:
                # In mininet.node.Switch which is parent-class of OVSBridge defines switch datapath_id (dpid)
                # automatically from `dpid` arg or switch name if dpid arg is not specified.
                # So, With OVSBridge, it need a switch name like "sw23" alphabet and number switch name.
                # To eliminate this restriction, It gives dummy dpid number.
                auto_dpid = "%016x" % index
                print("# add node %s as switch (dpid=%s)" % (node.name, auto_dpid))
                self.addSwitch(node.name, cls=ExtendedOVSBridge, dpid=auto_dpid, stp=node.stp)
            else:
                print("# Warning: Found unknown type node: %s (type: %s)" % (node.name, node.type), file=sys.stderr)

    def _build_links(self):
        for link in self._topology.links:
            print("# add link %s" % link)
            self.addLink(link.tp1.node, link.tp2.node, intfName1=link.tp1.intf, intfName2=link.tp2.intf)
