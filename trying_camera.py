import cv2
from camera import VideoCamera

# creates a camera object, don't flip vertically
video_camera = VideoCamera(
	flip = False, 
	usePiCamera = False, 
	resolution = (640, 480),
	record = True,
	record_duration = "00:05:00" # "HH:MM:SS"
	) 


while True:
	frame = video_camera.read()
	cv2.imshow("frame", frame)
	# no fps version
	#k = cv2.waitKey(int(1000/30)) & 0xff
	# accounting for fps in writer
	k = cv2.waitKey(1) & 0xff
	if k == 27:
		break
