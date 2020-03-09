# This script will allow preview from a camera object

from camera import VideoCamera
import cv2

cam = VideoCamera(
	flip = False, 
	usePiCamera = False, 
	resolution = (640, 480),
	record = False,
	record_timestamp = True
	)

while(True):
	
	cv2.imshow("preview", cam.read())
	k = cv2.waitKey(1)
	cv2.putText(frame, "Preview:",(10, 50),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1)
	cv2.putText(frame, "press 'q' to quit",(10, 100),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1)
	if k == ord("q"):
		break

cv2.destroyAllWindows()