#!/bin/bash

# clear all
iptables -F

# set policy
iptables -P INPUT ACCEPT
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# FORWARD
iptables -A FORWARD -p icmp -j ACCEPT
iptables -A FORWARD -s 192.168.0.0/24 -d 172.16.0.2/32 -p tcp --dport 8000 -j ACCEPT
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
