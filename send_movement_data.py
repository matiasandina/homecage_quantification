# this script sends the movement data to central computer
import argparse
import os
import numpy as np

# We will use this helper function to get the full path of the video files
def listdir_fullpath(root_dir, file_extension=None, exclude_dir = True):

    # Get everything
    if file_extension is None:
        a = [os.path.join(root_dir, files) for files in os.listdir(root_dir)]
    else:
        a = [os.path.join(root_dir, files) for files in os.listdir(root_dir) if files.endswith(file_extension)]

    if len(a) > 0:
        if exclude_dir:
            files_to_keep = np.bitwise_not(map(os.path.isdir, a))
            a = np.array(a)[files_to_keep]
            a = a.tolist()

    return sorted(a)

def send_data(date):
	# figure out date
	# ls all files with the particular date
	files = listdir_fullpath("~/homecage_quantification", file_extension=".txt")
	print(files)

	#cmd_command = "scp ~/homecage_quantification/ choilab@10.93.6.88:~/raspberry_IP/$MAC"
	#os.system()


if __name__ == '__main__':
	# construct the argument parser and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-date", "--date", required=True,
	help="date to match against all the movement files")
	args = vars(ap.parse_args())
	send_data(date = args["date"])