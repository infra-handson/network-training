#!/bin/bash

nsexec="ip netns exec"
for host in h2a h2b h3a h3b h4a h4b
do
  for addr in 203.0.113.13 172.16.0.66 172.16.0.130 172.16.0.138
  do
    echo "$nsexec $host curl -s -m 2 http://$addr/ 2>&1"
    echo "$nsexec $host curl -s -m 2 http://$addr:22/ 2>&1"
  done
done
