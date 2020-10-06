#!/bin/bash

prtintf "%-15s%5s\n" "TIMESTAMP" "Temp"
printf "%20s\n" "----------------------"

while true
do
		temp=$(vcgencmd measure_temp)
		timestamp=$(date)
		printf "%-15s%5s\n" "$timestamp" "$temp"
		sleep 10
done
