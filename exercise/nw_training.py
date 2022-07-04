#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""Run defined network"""

import argparse
import os
import re
import subprocess
import sys

from mn_builder.declared_topology import DeclaredTopology
from mn_builder.network_constructor import NetworkConstructor


if __name__ == "__main__":
    # delete proxy related environment keys
    proxy_vars = [v for v in os.environ if re.search(r"(ftp|https?)_proxy", v, flags=re.IGNORECASE)]
    for var in proxy_vars:
        del os.environ[var]

    parser = argparse.ArgumentParser(description="Network Training Environment Interpreter")
    parser.add_argument("topology", help="Training network declaration (json file)")
    parser.add_argument("-l", "--loglevel", default="info", help="Log level")
    args = parser.parse_args()

    try:
        # set flag to enable iptables LOG action (logging) in netns
        # see: networking - Iptables LOG rule inside a network namespace - Server Fault
        # https://serverfault.com/questions/691730/iptables-log-rule-inside-a-network-namespace
        # subprocess.call(["sysctl", "-w", "net.netfilter.nf_log_all_netns=1"])

        # set `rp_filter` (Reverse Path Filter) to 2 (RFC3704 Loose Reverse Path)
        # to enable asymmetric routing.
        # see: 戻り経路フィルタ (Reverse Path Filtering)
        # https://linuxjf.osdn.jp/JFdocs/Adv-Routing-HOWTO/lartc.kernel.rpf.html
        # see: https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt
        subprocess.call(["sysctl", "-w", "net.ipv4.conf.all.rp_filter=2"])
        subprocess.call(["sysctl", "-w", "net.ipv4.conf.default.rp_filter=2"])

        declared_topology = DeclaredTopology(args.topology)
        nw_constructor = NetworkConstructor(declared_topology, args.loglevel)
        nw_constructor.run()
    except OSError as error:
        print("Warning:  OSError was raised but ignored: %s" % error)
        subprocess.call(["mn", "-c"])
        # clear all network namespace links to access it from external of mininet-CLI.
        subprocess.call(["rm", "-rf", "/var/run/netns/*"])
        sys.exit(0)
