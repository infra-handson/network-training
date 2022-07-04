"""node class"""

# pylint: disable=import-error
from declared_interface import DeclaredTopologyIntf


class DeclaredTopologyRoutes:
    """route (static route) class"""

    def __init__(self, route_dict):
        self._dict = route_dict

    @property
    def dst_net(self):
        """destination (target) network"""
        return self._dict["dst_net"]

    @property
    def next_hop(self):
        """next hop gateway address"""
        return self._dict["next_hop"]

    @property
    def is_default(self):
        """check the route is default route ('default' keyword)"""
        return self.dst_net == "default"

    def __str__(self):
        return "[%s > %s]" % (self.dst_net, self.next_hop)


class DeclaredTopologyNode:
    """Any type of node for declared topology (topology definition)"""

    def __init__(self, node_dict):
        self._dict = node_dict
        self._stp = bool(self._dict["stp"]) if "stp" in self._dict else False
        self._stp_priority = self._dict["stp_priority"] if "stp_priority" in self._dict else 0x8000
        self._svc_procs = self._dict["svc_procs"] if "svc_procs" in self._dict else []
        self._routes = self._convert_routes(node_dict)
        self._interfaces = self._convert_interfaces(node_dict)

    def _convert_routes(self, node_dict):
        # when switch type node, 'routes' is ignored.
        # 'routes' in node is optional section
        if self.is_switch or "routes" not in node_dict:
            return []

        return [DeclaredTopologyRoutes(route) for route in node_dict["routes"]]

    @staticmethod
    def _convert_interfaces(node_dict):
        return [DeclaredTopologyIntf(intf) for intf in node_dict["interfaces"]]

    @property
    def name(self):
        """node name"""
        return self._dict["name"]

    @property
    def type(self):
        """node type"""
        return self._dict["type"]

    @property
    def svc_procs(self):
        """process to exec in this node (server process)"""
        return self._svc_procs

    @property
    def routes(self):
        """list of static route"""
        return self._routes

    @property
    def interfaces(self):
        """list of interface"""
        return self._interfaces

    @property
    def sub_interfaces(self):
        """list of sub-interface"""
        interfaces_has_sub_intf = [intf for intf in self.interfaces if intf.has_sub_interfaces]
        # list(list(sub-interface))
        sub_interfaces_list = [intf.sub_interfaces for intf in interfaces_has_sub_intf]
        return sum(sub_interfaces_list, [])  # flatten

    @property
    def is_router(self):
        """check this node is router"""
        return self.type == "router"

    @property
    def is_host(self):
        """check this node is host (endpoint node)"""
        return self.type == "host"

    @property
    def is_switch(self):
        """check this node is L2 switch"""
        return self.type == "switch"

    def intf(self, name):
        """find interface by name"""
        return next((intf for intf in self.interfaces if intf.name == name), None)

    @property
    def stp(self):
        """stp mode (enable if True)"""
        return self._stp

    @property
    def stp_priority(self):
        """stp bridge priority"""
        return self._stp_priority

    def has_intf(self, name):
        """check this node has specified interface"""
        return bool(self.intf(name))
