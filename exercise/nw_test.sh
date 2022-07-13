#!/usr/bin/bash

function run_test() {
  dir=$1
  file=$2
  vars=$3
  goss_file="$dir/$file.goss.yaml"
  vars_file="$dir/$vars.vars.yaml"
  goss -g "$goss_file" --vars "$vars_file" validate
}

case "$1" in
  "l3nw2")
    run_test l3nw2 l3 l3
    ;;
  "l4nw1"|"l4nw3")
    run_test l4nw1 l4 l4
    ;;
  "app1_l3")
    echo "# L3 success case test"
    run_test app1 l3_success success
    echo "# L3 fail case test"
    run_test app1 l3_fail fail
    ;;
  "app1_l4")
    echo "# L4 success case test"
    run_test app1 l4_success success
    echo "# L4 fail case test"
    run_test app1 l4_fail fail
    ;;
  *)
    echo "Unknown scenario name to test: $1"
    exit 1
    ;;
esac
