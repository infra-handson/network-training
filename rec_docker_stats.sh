#!/bin/bash

interval=10 # sec
format_body="{{.ID}}, {{.Name}}, {{.CPUPerc}}, {{.MemUsage}}, {{.MemPerc}}, {{.NetIO}}, {{.BlockIO}}, {{.PIDs}}"
# shellcheck disable=SC2001
header_body=$(echo "$format_body" | sed -e 's/[\.{}]//g')
log_file=docker_stats_$(date +%Y%m%d-%H%M%S).log

echo "DateTime, $header_body" | tee "$log_file"
while true; do
  echo "---"
  date_str=$(date --iso-8601=second)
  docker stats --format="$date_str, $format_body" --no-stream | tee --append "$log_file"
  sleep $interval
done
