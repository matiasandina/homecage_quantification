import numpy as np
import psutil
import os
import time
import datetime

# This script monitors system status for RPi
# 1) cpu usage
# 2) ram usage
# 3) temperature

# create lists
# TODO: change this to deque if you are concerned about stack issues
datetime_list = []
cpu_list = []
cpu_temp_list = []
mean_cpu_list = []
ram_list = []


while True:
	dt = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
	# cpu usage
	cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
	mean_cpu = np.mean(cpu_percent)
	# cpu temp
	# this works for RPi, sensors_temperatures returns a dict 
	cpu_temp = psutil.sensors_temperatures()["cpu-thermal"][0].current
	# we could also use bash
	#cpu_temp = os.popen("vcgencmd measure_temp | egrep -o '[0-9]*\.[0-9]*'").read().replace("\n", "")
	# ram
	ram = psutil.virtual_memory().percent

	# do some printing
	print(dt, cpu_percent, mean_cpu, "%", ram, "% RAM", cpu_temp, "Celsius")

	# do the appending
	datetime_list.append(dt)
	cpu_list.append(cpu_percent)
	mean_cpu_list.append(mean_cpu)
	cpu_temp_list.append(cpu_temp)
	ram_list.append(ram)

	# sleep 10 seconds
	time.sleep(10)