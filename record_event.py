import cv2
from camera import VideoCamera

# creates a camera object, don't flip vertically
video_camera = VideoCamera(
	flip = False, 
	usePiCamera = False, 
	resolution = (640, 480),
	record = True,
	record_timestamp = False,
	record_duration = "00:05:00" # "HH:MM:SS"
	) 

def record_event():
	while True:
		frame = video_camera.read()
		cv2.imshow("frame", frame)
		# no fps version
		#k = cv2.waitKey(int(1000/30)) & 0xff
		# accounting for fps in writer
		k = cv2.waitKey(1) & 0xff
		# we don't want accidental breaks 
		# people can always do keyboard interrupt
		#if k == 27:
		#	break


if __name__ == '__main__':
	record_event()