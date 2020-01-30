import cv2
from imutils.video import VideoStream
import imutils
import time
import numpy as np
import datetime

class VideoCamera(object):
    def __init__(
    self,
    flip = False, usePiCamera = True,
    resolution = (640, 480),
    record = False, record_duration = None, record_timestamp = True
    ):

        self.vs = VideoStream(usePiCamera = usePiCamera, resolution = resolution).start()
        self.flip = flip
        # Record settings ###
        # no recording set at init
        self.rec_set = False
        # trigger record
        self.trigger_record = record
        self.resolution = resolution
        self.fps = 20.0
        time.sleep(2.0)
        # we might be in trouble if we switch from color to grayscale
        self.isColor = self.is_color()
        self.record_start = None
        if (record_duration is not None):
            session_time = datetime.datetime.strptime(record_duration, '%H:%M:%S')
            # Transform the time into number of steps
            seconds = (session_time.hour * 60 + session_time.minute) * 60 + session_time.second
            self.record_duration = seconds
        self.record_timestamp = record_timestamp


    def __del__(self):
        self.vs.stop()

    def is_color(self):
        frame = self.vs.read()
        if (len(frame.shape) == 3):
            return True
        else:
            return False


    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def read(self):
        # this is the read function we want to do processing
        frame = self.flip_if_needed(self.vs.read())
        if (self.trigger_record):
            if (self.record_timestamp):
                stamp = str(datetime.datetime.now())
                cv2.putText(frame, stamp,
                    (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1,
                    (255,255,255),
                    1)
            self.record(frame)
        return frame

    def get_frame(self, label_time):
        # This function ends up converting to jpg and timestamping
        # intended for streaming 
        frame = self.flip_if_needed(self.vs.read())
        if (label_time):
            cv2.putText(frame, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                (10, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1,
                (255,255,255),
                1)    

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def get_object(self, classifier):
        found_objects = False
        frame = self.flip_if_needed(self.vs.read()).copy() 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        objects = classifier.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(objects) > 0:
            found_objects = True

        # Draw a rectangle around the objects
        for (x, y, w, h) in objects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return (jpeg.tobytes(), found_objects)


    def record(self, frame):
        """
        Opencv VideoWriter
        https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
        This time we create a VideoWriter object. 
        We should specify the output file name (eg: output.avi).
        Then we should specify the FourCC code (details in next paragraph).
        Then number of frames per second (fps) and frame size should be passed.
        And last one is isColor flag. If it is True, encoder expect color frame,
        otherwise it works with grayscale frame.

        Example comes from here
        https://stackoverflow.com/questions/30509573/writing-an-mp4-video-using-python-opencv
        """
        if (self.rec_set == False):
            # we will use timestamps to prevent overwriting
            self.name = str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")) + "_output.avi"
            self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.recorder = cv2.VideoWriter(self.name, self.fourcc, self.fps, self.resolution, self.isColor)
            self.rec_set = True
            self.prev_frame = time.time()
            self.record_start = self.prev_frame
            # Write first frame
            self.recorder.write(frame)

        else:
            # account for fps
            # otherwise, we would need to account for this via waitKey(int(1000/fps)) 
            current_frame = time.time()
            if (current_frame - self.prev_frame > 1/self.fps):
                self.recorder.write(frame)
                self.prev_frame = current_frame

            if (self.prev_frame - self.record_start > self.record_duration):
                print(self.prev_frame)
                print(self.record_start)
                print(self.record_duration)
                # stop the recording (not the camera)
                self.trigger_record = False
