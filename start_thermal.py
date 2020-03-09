# This script will allow you to trigger the openMV board
# It will automatically stop after a number of retries

import sys, serial, struct
import datetime
import time

port = '/dev/ttyACM0'
# port might be having issues, like being busy/delayed
prort_ready = False
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


retry_num = 0
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
		time.sleep(1)

	# manage exit
	retry_num = retry_num + 1
	if (retry_num > 100):
		print("Tried too many times, check connection and restart script from console.")
		break
