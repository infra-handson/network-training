#!/bin/bash

OUTPUT_DIR="./exercise"
INPUT_DIR="./exercise_docs"

shopt -s globstar nullglob
for yaml_path in "$INPUT_DIR"/**/*.yaml
do
  yaml_file=$(basename "$yaml_path")
  exercise_name=$(basename $(dirname "$yaml_path"))
  json_file=${yaml_file%.yaml}.json # replace suffix

  echo "---"
  echo "# Test $yaml_path"
  ./topology_checker.py "$yaml_path" | grep -vi info
  echo "# Convert $yaml_path to $OUTPUT_DIR/$exercise_name/$json_file"
  mkdir -p "$OUTPUT_DIR/$exercise_name"
  ./topology_checker.py "$yaml_path" -o json > "$OUTPUT_DIR/$exercise_name/$json_file"
done
