# This script will trigger camera pictures every x seconds

import sys, serial, struct
import datetime
import time
import signal
from collections import deque
import numpy as np

class Thermal():
	"""docstring for Thermal"""
	def __init__(self):
		super(Thermal, self).__init__()
		
	def save_deque(self):
		# because we are clearing the deque each time
		# we don't have to worry about having unsaved elements
	    #print("Saving thermal timestap on iteration..." + str(samples[-1]))
	    # array with timestamp and deque to save, transpose for having them as cols
	    d = np.array([self.samples, self.timestamps]).T
	    with open(self.filename,'a') as outfile:
	        np.savetxt(outfile, d,
	        delimiter=',', fmt='%s')
	    return

	def exit_gracefully(self, *args):
		self.save_deque()
		sys.exit(0)

	def run(self, seconds_delay = 0.5):

		signal.signal(signal.SIGINT, self.exit_gracefully)
		signal.signal(signal.SIGTERM, self.exit_gracefully)

		self.samples = deque(maxlen=10)
		self.timestamps = deque(maxlen = 10)

		#while(prort_ready is False):
		#	try:
		#		sp = serial.Serial(port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
		#				xonxoff=False, rtscts=False, stopbits=serial.STOPBITS_ONE, timeout=None, dsrdtr=False)
		#		# break
		#		prort_ready = sp.isOpen()
		#	except:
		#		print("Port busy or unplugged, retrying in two seconds")
		#		time.sleep(2)
		#		pass

		sample_num = 1
		while(True):
			if True:#sp.isOpen() == True:
				#sp.setDTR(True) # dsrdtr is ignored on Windows.
				#print('Sending command')
				print(sample_num)

				# get the date 
				now = datetime.datetime.now()#.isoformat()
				# we send subsecond 0 for simplicity, we don't need to be THAT accurate
				# year, month, day, weekday, hour, minute, second, subsecond
				message = (now.year, now.month, now.day, now.isoweekday(), now.hour, now.minute, now.second, 0)
				# paste date so we can parse
				message = "date: " + str(message)
				print(message.encode())
				#sp.write(message.encode())
				# create_filename
				if sample_num == 1:
					self.filename = now.strftime("%Y-%m-%dT%H-%M-%S") + "_thermal_timestamps.csv.gz"
				# append to deques
				self.samples.append(sample_num)
				self.timestamps.append(now)

				if sample_num % 10 == 0:
					self.save_deque()
					# reset values
					self.samples.clear()
					self.timestamps.clear()
				# increase counter
				sample_num = sample_num + 1
				# sleep using delay
				time.sleep(seconds_delay)

if __name__ == '__main__':
	thermal = Thermal()
	thermal.run()