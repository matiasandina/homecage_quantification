# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import pandas as pd
import os
import itertools
from ast import literal_eval

# Helper to Save the thing
def save_data(filename):
	with open(filename,'a') as outfile:
		np.savetxt(outfile, mouse_pts,
		delimiter=',', fmt='%s')

# Helper to parse arguments
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
				help="path to the (optional) video file. If not provided goes to webcam")
ap.add_argument("-blackLower", "--blackLower", required=True,
				help="HSV coordinates for low threshold as string of tupple (e.g, (50, 0, 50))")
ap.add_argument("-blackUpper", "--blackUpper", required=True,
				help="HSV coordinates for high threshold as string of tupple (e.g, (255, 255, 255))")
ap.add_argument("-b", "--buffer", type=int, default=100,
				help="max buffer size")
args = vars(ap.parse_args())

# Main function

# Mask parameters #####
# define the lower and upper boundaries of the marbles
# We only need to modify value in the HSV

### USE range_detector.py to choose appropriate HSV values

# blackLower = (0, 0, 0)
# blackUpper = (255, 255, 40)

blackLower = args["blackLower"]
blackUpper = args["blackUpper"]

# We need the literal evaluation of the above strings

blackLower = literal_eval(blackLower)
blackUpper = literal_eval(blackUpper)

# Validate blackLower and blackUpper

# if not(low_threshold < med_threshold):
#	raise Exception("low_threshold must be smaller than med_threshold")

# if(low_threshold > 1.0 or med_threshold > 1.0):
#	raise Exception("low_threshold and med_threshold are floats bound between 0 and 1")


# Create a bucket to store the centroids and number of marbles
frame_pts = deque(maxlen=args["buffer"])
mouse_pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
	vs = VideoStream(src=0).start()

# otherwise, grab a reference to the video file
else:
	vs = cv2.VideoCapture(args["video"])
	# We will save a file with time as id

# Get number of frames ?
# video_length = int(vs.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

# allow the camera or video file to warm up
time.sleep(2.0)

# set the counters
iteration_number = 1

# keep looping
while True:

	# grab the current frame
	frame = vs.read()

	# handle the frame from VideoCapture or VideoStream
	frame = frame[1] if args.get("video", False) else frame

	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if frame is None:
		break

	# resize the frame, blur it, and convert it to the HSV
	# color space
	# frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a mask for the marbles and mice, then perform

	binarymask = cv2.inRange(hsv, blackLower, blackUpper)

	kernel = np.ones((5, 5), np.uint8)

	# Do some erosion-dilation to clear noise (hopefully ears)
	mask = cv2.erode(binarymask, kernel, iterations=2)
	mask = cv2.dilate(binarymask, kernel, iterations=2)

	# Marbles have holes inside, we will close them
	mask = cv2.morphologyEx(binarymask, cv2.MORPH_CLOSE, kernel)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(),
							cv2.RETR_EXTERNAL,
							cv2.CHAIN_APPROX_SIMPLE)

	# This is a function that checks the length of contours
	# it is related to the opencv version we are using

	cnts = imutils.grab_contours(cnts)

	# mouse center

	c = max(cnts, key=cv2.contourArea)
	((x, y), radius) = cv2.minEnclosingCircle(c)
	M = cv2.moments(c)
	mouse_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
	# For the mouse only proceed if the radius meets a minimum size
	if radius > 10:
		# draw the circle and centroid on the frame,
		# then update the list of tracked points
		cv2.circle(frame,
				   (int(x), int(y)),  # centroid (x,y) coordinates
				   int(radius),  # radius
				   (0, 255, 255),  # yellow circle
				   2)  # thickness

		cv2.circle(frame, mouse_center,
				   5,  # a very small circle
				   (0, 0, 255),  # in red
				   -1)  # Negative thickness means that a filled circle is to be drawn.

	# update the points queue
	frame_pts.append(iteration_number)
	mouse_pts.append(mouse_center)

	# Display a piece of the track
	# loop over the set of tracked points
	for i in range(1, len(mouse_pts)):
		# if either of the tracked points are None (aka first and last frames), ignore
		# them
		if mouse_pts[i - 1] is None or mouse_pts[i] is None:
			continue

		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int((float(i + 1) / args["buffer"]) * 2.5) + 1
		cv2.line(frame,
				 mouse_pts[i - 1],  # from
				 mouse_pts[i],  # to
				 (0, 0, 255),  # in red
				 thickness)

	# Convert to array to save
	# Wait until the iteration number is divisible by the buffer length
	if (iteration_number % args["buffer"] == 0):
		last_saved = iteration_number
		print("Saving on iteration..." + str(last_saved))
		# Call helper to save
		save_data('mouse_track.csv')

	# Add if statement to avoid showing videos for efficiency
	# show the videos to our screen
	cv2.imshow("Frame", frame)
	cv2.imshow("Mask", mask)

	# Add 1 to the counter
	iteration_number = iteration_number + 1

	#### Kill the process ######
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
	vs.stop()

# otherwise, release the camera
else:
	vs.release()

# close all windows
cv2.destroyAllWindows()
