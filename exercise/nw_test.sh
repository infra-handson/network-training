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
  "l3nw_2")
    run_test l3nw_2 l3nw_2 l3nw_2
    ;;
  "l4nw_1"|"l4nw_3")
    run_test l4nw_1 l4nw_1 l4nw_1
    ;;
  "app_1_l3")
    echo "# L3 success case test"
    run_test app_1 app_1_l3s app_1s
    echo "# L3 fail case test"
    run_test app_1 app_1_l3f app_1f
    ;;
  "app_1_l4")
    echo "# L4 success case test"
    run_test app_1 app_1_l4s app_1s
    echo "# L4 fail case test"
    run_test app_1 app_1_l4f app_1f
    ;;
  *)
    echo "Unknown scenario name to test: $1"
    exit 1
    ;;
esac
