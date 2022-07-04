#!/bin/bash

for prot in http ssh
do
  for server in inet:Internet s0a:Server0a s1a:Server1a s1b:Server1b s1c:Server1c
  do
    short=$(echo "$server" | cut -d: -f1)
    long=$(echo "$server" | cut -d: -f2)
    docroot_dir="docroot-${short}-${prot}"
    mkdir -p "$docroot_dir"
    content_str="${long} - ${prot}"
    echo "$content_str" > "$docroot_dir"/index.html
    echo "" >> "$docroot_dir"/index.html
    figlet -f smslant "$content_str" >> "$docroot_dir"/index.html
  done
done
