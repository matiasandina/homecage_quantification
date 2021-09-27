# This script will trigger camera pictures every x seconds

import sys, serial, struct
import datetime
import time
import signal
from collections import deque
import numpy as np

def save_deque(samples, timestamps, filename):
	# because we are clearing the deque each time
	# we don't have to worry about having unsaved elements
    #print("Saving thermal timestap on iteration..." + str(samples[-1]))
    # array with timestamp and deque to save, transpose for having them as cols
    d = np.array([samples, timestamps]).T
    with open(filename,'a') as outfile:
        np.savetxt(outfile, d,
        delimiter=',', fmt='%s')
    return

def exit_gracefully(self, *args):
	save_deque(samples, timestamps, filename)
    sys.exit(0)

def run(seconds_delay = 30):
	signal.signal(signal.SIGINT, exit_gracefully)
	signal.signal(signal.SIGTERM, exit_gracefully)

	while(prort_ready is False):
		try:
			sp = serial.Serial(port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
					xonxoff=False, rtscts=False, stopbits=serial.STOPBITS_ONE, timeout=None, dsrdtr=False)
			# break
			prort_ready = sp.isOpen()
		except:
			print("Port busy or unplugged, retrying in two seconds")
			time.sleep(2)
			pass

	samples = deque(maxlen=10)
	timestamps = deque(maxlen = 10)

	sample_num = 1
	while(True):
		if sp.isOpen() == True:
			sp.setDTR(True) # dsrdtr is ignored on Windows.
			#print('Sending command')

			# get the date 
			now = datetime.datetime.now()#.isoformat()
			# we send subsecond 0 for simplicity, we don't need to be THAT accurate
			# year, month, day, weekday, hour, minute, second, subsecond
			message = (now.year, now.month, now.day, now.isoweekday(), now.hour, now.minute, now.second, 0)
			# paste date so we can parse
			message = "date: " + str(message)
			print(message.encode())
			sp.write(message.encode())
			sample_num = sample_num + 1
			# create_filename
			if sample_num == 1:
				filename = now.strftime("%Y-%m-%dT%H-%M-%S") + "_thermal_timestamps.csv.gz"

			# append to deques
			samples.append(sample_num)
			timestamps.append(now)

			if sample_num % 10 == 0:
				save_deque(samples, timestamps, filename)
				# reset values
				samples.clear()
				timestamps.clear()
			# sleep using delay
			time.sleep(seconds_delay)

if __name__ == '__main__':
	run()