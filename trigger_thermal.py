# This script will trigger camera pictures every x seconds

import sys, serial, struct
import datetime
import time
import signal


def exit_gracefully(self, *args):
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

			time.sleep(seconds_delay)

if __name__ == '__main__':
	run()