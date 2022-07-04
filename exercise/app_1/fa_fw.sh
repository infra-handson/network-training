#!/bin/bash

# clear all
iptables -F

# set policy
iptables -P INPUT ACCEPT
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# FORWARD
iptables -A FORWARD -p icmp -s 172.16.0.0/12 -j ACCEPT
iptables -A FORWARD -p icmp -d 172.16.0.64/26 -j ACCEPT
iptables -A FORWARD -p tcp -s 172.16.0.0/12 --dport 80 -j ACCEPT
iptables -A FORWARD -p tcp -d 172.16.0.64/26 --dport 80 -j ACCEPT
iptables -A FORWARD -p tcp -s 172.16.1.32/27 -d 172.16.0.64/29 --dport 22 -j ACCEPT
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

iptables -A FORWARD -p tcp -s 172.16.0.64/29 -d 172.16.0.0/12 -j REJECT
iptables -A FORWARD -p udp -s 172.16.0.64/29 -d 172.16.0.0/12 -j REJECT
iptables -A FORWARD -j REJECT
