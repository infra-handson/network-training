#!/bin/bash

OUTPUT_DIR="./exercise"
INPUT_DIR="./exercise_docs"

shopt -s globstar nullglob
for yaml_path in "$INPUT_DIR"/**/*.yaml
do
  yaml_file=$(basename "$yaml_path")
  drill_name=${yaml_file%.*} # file name without suffix
  json_file=${yaml_file%.yaml}.json # replace suffix

  if [[ $drill_name =~ ^(.*_[0-9]+)[a-z]+$ ]]; then
    drill_name=${BASH_REMATCH[1]}
  fi
  drill_dir="$OUTPUT_DIR/$drill_name"

  echo "---"
  echo "# Test $yaml_path"
  ./topology_checker.py "$yaml_path" | grep -vi info
  echo "# Convert $yaml_path to $drill_dir/$json_file"
  mkdir -p "$drill_dir"
  ./topology_checker.py "$yaml_path" -o json > "$drill_dir/$json_file"
done
