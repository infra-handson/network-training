#!/bin/bash

# clear all
iptables -F

# set policy
iptables -P INPUT ACCEPT
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# FORWARD
iptables -A FORWARD -p icmp -j ACCEPT
iptables -A FORWARD -p tcp -j ACCEPT
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -j REJECT
