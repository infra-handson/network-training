"""Link class"""


class DeclaredTopologyIntfRef:
    """Reference pointer of interface"""

    def __init__(self, node, intf):
        self._node = node
        self._intf = intf

    @property
    def node(self):
        """reference: node name"""
        return self._node

    @property
    def intf(self):
        """reference: interface name"""
        return self._intf

    def __str__(self):
        return "%s[%s]" % (self.node, self.intf)

    def __eq__(self, other):
        return self.node == other.node and self.intf == other.intf


class DeclaredTopologyLink:
    """Any type of link for declared topology (topology definition)"""

    def __init__(self, link_dict):
        self._tp1 = DeclaredTopologyIntfRef(link_dict["node1"], link_dict["intf1"])  # termination point 1
        self._tp2 = DeclaredTopologyIntfRef(link_dict["node2"], link_dict["intf2"])  # termination point 2
        self._down = bool(link_dict["down"]) if "down" in link_dict else False

    @property
    def is_down_in_initial(self):
        """the link is disabled(down) when initialized"""
        return self._down

    @property
    def tp1(self):
        """term-point-1"""
        return self._tp1

    @property
    def tp2(self):
        """term-point-2"""
        return self._tp2

    def connected_to(self, node_name, intf_name):
        """make link: connect self and specified node/interface"""
        tp_ref = DeclaredTopologyIntfRef(node_name, intf_name)
        return tp_ref in (self.tp1, self.tp2)

    def __str__(self):
        return "%s <=> %s" % (self.tp1, self.tp2)

    def __eq__(self, other):
        return self.tp1 == other.tp1 and self.tp2 == other.tp2 or self.tp1 == other.tp2 and self.tp2 == other.tp1
