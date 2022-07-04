#!/bin/bash

# clear all
iptables -F

# set policy
iptables -P INPUT ACCEPT
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# FORWARD
iptables -A FORWARD -p icmp -j ACCEPT
iptables -A FORWARD -p tcp -s 172.16.1.128/25 --dport 80 -j ACCEPT
iptables -A FORWARD -p tcp -s 172.16.1.128/25 -d 172.16.0.136/29 --dport 8000 -j ACCEPT
## begin ANSWER
iptables -A FORWARD -p tcp -s 172.16.1.128/25 -d 172.16.0.144/29 --dport 8000 -j ACCEPT
iptables -A FORWARD -p tcp -s 172.16.1.64/26 --dport 80 -j ACCEPT
iptables -A FORWARD -p tcp -s 172.16.1.64/26 -d 172.16.0.136/29 --dport 8000 -j ACCEPT
iptables -A FORWARD -p tcp -s 172.16.1.64/26 -d 172.16.0.144/29 --dport 8000 -j ACCEPT
## end ANSWER
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -j REJECT
