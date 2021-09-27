# This script will allow preview from a camera object

from camera import VideoCamera
import cv2
import signal

cam = VideoCamera(
	flip = False, 
	usePiCamera = False, 
	resolution = (640, 480),
	record = False,
	record_timestamp = True
	)

def exit_gracefully(self, *args):
    cv2.destroyAllWindows()
    sys.exit(0)

def run():
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    while(True):
        frame = cam.read()
        cv2.putText(frame, "Preview:",(10, 50),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1)
        cv2.putText(frame, "press 'q' to quit",(10, 100),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1)
        cv2.imshow("preview", frame)
        k = cv2.waitKey(1)
        if k == ord("q"):
            break
    cv2.destroyAllWindows()

if __name__ == '__main__':
	run()
