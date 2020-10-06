#!/bin/bash

printf "%-15s%5s\n" "TIMESTAMP" "Temp"
printf "%20s\n" "----------------------"

while true
do
		# get temp and only the numeric values
		temp=$(vcgencmd measure_temp | egrep -o '[0-9]*\.[0-9]*')
		timestamp=$(date)
		printf "%-15s%5s\n" "$timestamp" "$temp"
		sleep 10
done
