"""Interface class"""

from abc import ABCMeta
import re


class DeclaredIntfBase:
    """Base interface class"""

    __metaclass__ = ABCMeta

    def __init__(self, intf_dict):
        self._dict = intf_dict
        self._mac_addr = self._dict["mac_addr"] if self.use_fixed_mac_addr else ""

    @property
    def name(self):
        """interface name"""
        return self._dict["name"]

    @property
    def use_fixed_mac_addr(self):
        """check fixed mac-address to interface"""
        return "mac_addr" in self._dict

    @property
    def mac_addr(self):
        """interface mac address (empty-string means auto and random)"""
        return self._mac_addr

    @property
    def is_valid_veth_name(self):
        """validate veth interface name"""
        if not re.fullmatch(r"[a-zA-Z0-9._-]{0,15}", self.name):
            return False

        return True


class DeclaredTopologySubIntf(DeclaredIntfBase):
    """sub-interface class"""

    def __init__(self, sub_intf_dict):
        # pylint: disable=super-with-arguments
        super(DeclaredTopologySubIntf, self).__init__(sub_intf_dict)
        self._define_opt_property_name()

    def _define_opt_property_name(self):
        # 'name' section is optional, generate automatically if name is not specified.
        if "name" in self._dict:
            self._name = self._dict["name"]
        else:
            self._name = "%s.%d" % (self._dict["_parent_name_"], self.vlan)

    @property
    def name(self):
        """sub-interface name"""
        return self._name

    @property
    def ip_addr(self):
        """sub-interface ip address"""
        return self._dict["ip_addr"]

    @property
    def vlan(self):
        """sub-interface vlan id"""
        return self._dict["vlan"]

    @property
    def parent_intf_name(self):
        """parent interface name of this sub-interface"""
        return self._dict["_parent_name_"]


class DeclaredTopologyIntf(DeclaredIntfBase):
    """Any type of interface for declared topology (topology definition)"""

    def __init__(self, intf_dict):
        # pylint: disable=super-with-arguments
        super(DeclaredTopologyIntf, self).__init__(intf_dict)
        self._ip_addr = self._dict["ip_addr"] if self.is_l3 else ""
        self._access_vlan = self._dict["access_vlan"] if self.is_l2 and "access_vlan" in self._dict else 0
        self._trunk_vlans = self._dict["trunk_vlans"] if self.is_l2 and "trunk_vlans" in self._dict else []
        self._define_opt_property_sub_interfaces()

    def _define_opt_property_sub_interfaces(self):
        self._sub_interfaces = []  # default
        if "sub_interfaces" not in self._dict:
            return

        for sintf in self._dict["sub_interfaces"]:
            sintf["_parent_name_"] = self.name  # add parent interface name
        self._sub_interfaces = [DeclaredTopologySubIntf(sintf) for sintf in self._dict["sub_interfaces"]]

    @property
    def type(self):
        """interface type (L2 or L3)"""
        return self._dict["type"]

    @property
    def is_l2(self):
        """check interface type is L2"""
        return self.type == "l2"

    @property
    def is_l3(self):
        """check interface type is L3"""
        return self.type == "l3"

    @property
    def ip_addr(self):
        """interface ip address"""
        return self._ip_addr

    @property
    def access_vlan(self):
        """interface vlan id"""
        return self._access_vlan

    @property
    def trunk_vlans(self):
        """vlan id list of this trunk port"""
        return self._trunk_vlans  # List of integer

    @property
    def trunk_vlans_str(self):
        """string-expression of vlan id list of this trunk port"""
        return ",".join([str(v) for v in self.trunk_vlans])  # "," separated trunk vlans string

    @property
    def has_l2_access_vlan_config(self):
        """check this interface has L2 access port config"""
        return self.is_l2 and self.access_vlan > 0

    @property
    def has_l2_trunk_vlans_config(self):
        """check this interface has L2 trunk port config"""
        return self.is_l2 and len(self.trunk_vlans) > 0

    @property
    def has_l2_vlan_config(self):
        """check this interface has L2 port config (trunk or access port)"""
        return self.has_l2_access_vlan_config or self.has_l2_trunk_vlans_config

    @property
    def sub_interfaces(self):
        """sub-interface list of this interface"""
        return self._sub_interfaces

    @property
    def has_sub_interfaces(self):
        """check this interface has sub interfaces"""
        return len(self.sub_interfaces) > 0

    def __str__(self):
        return "[%s {type:%s}]" % (self.name, self.type)

    @property
    def assumed_trunk_port(self):
        """
        check this interface works as a trunk port
        - Notice: sub-interfaces is allowed for l3-type interface.
        """
        return self.has_l2_trunk_vlans_config or self.has_sub_interfaces

    @property
    def any_trunk_vlans(self):
        """
        vlans the interface owns
        - type: l2 => trunk_vlans or sub-interfaces vlan
        - type: l3 => sub_interfaces vlan
        """
        if self.has_l2_trunk_vlans_config:
            return sorted(self.trunk_vlans)
        if self.has_sub_interfaces:
            return sorted([sintf.vlan for sintf in self.sub_interfaces])

        return []
