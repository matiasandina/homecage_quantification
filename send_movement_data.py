# this script sends the movement data to central computer
import argparse
import os
import numpy as np

# We will use this helper function to get the full path of the video files
def listdir_fullpath(root_dir, file_pattern=None, file_extension=None, exclude_dir = True):

	# Get everything
	if file_extension is None:
		file_list  = [os.path.join(root_dir, files) for files in os.listdir(root_dir)]
	else:
		file_list = [os.path.join(root_dir, files) for files in os.listdir(root_dir) if files.endswith(file_extension)]
	if file_pattern is not None:
			file_list = [file for file in file_list if file_pattern in file]
	if len(file_list) > 0:
		if exclude_dir:
			files_to_keep = np.bitwise_not(list(map(os.path.isdir, file_list)))
			file_list = np.array(file_list)[files_to_keep]
			file_list = file_list.tolist()

	return sorted(file_list)

def send_data(date):
	# get mac address
	# caution this only works for raspberry PIs on WiFI
	mac = open('/sys/class/net/wlan0/address').readline()
	# replace "\n" coming from readline()
	mac = mac.replace("\n", "")

	# figure out date
	# ls all files with the particular date
	files = listdir_fullpath("/home/pi/homecage_quantification/",
		file_pattern=date,
		file_extension=".csv")

	if len(files) > 0:
		for file in files:
			print(file)
			cmd_command = "scp " + file + " choilab@10.93.6.88:~/raspberry_IP/" + mac
			os.system(cmd_command)
	else:
		# some sort of warning here
		return()

	
if __name__ == '__main__':
	# construct the argument parser and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-date", "--date", required=True,
	help="date to match against all the movement files")
	args = vars(ap.parse_args())
	send_data(date = args["date"])