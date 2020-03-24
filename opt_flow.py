import cv2
import numpy as np
import imutils
import argparse
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from collections import deque
import datetime
import os

def exit_handler(iter_number, timestamp, mag_deque, maxlen, filename):
    print('Application is ending')
    print('Calling save_deque()')
    # save all deques
    save_deque(iter_number, timestamp, mag_deque, maxlen, filename) 
    cv2.destroyAllWindows()


def save_deque(iter_number, timestamp, deque_to_save, maxlen, filename):

    # iter_number[-1] is the last iteration if deque... here iternumber is an int
    # we could also do max(iter_number)

    unsaved_elements = iter_number % maxlen

    if (unsaved_elements == 0):
        print("Saving " + filename + " on iteration..." + str(iter_number))
        with open(filename,'a') as outfile:
            np.savetxt(outfile, deque_to_save,
            delimiter=',', fmt='%s')

    else:
        # convert to list and slice the last unsaved elements
        print("Saving rest of " + filename )
        rest = list(deque_to_save)[-unsaved_elements:]
        # Here we only save the rest 
        with open(filename,'a') as outfile:
            np.savetxt(outfile, rest,
            delimiter=',', fmt='%s')
    return


def opt_flow(cap, show_video, filename):
    # buffer size for keeping RAM smooth 
    maxlen = 1000
    mag_deque = deque(maxlen=maxlen)

    # grab the current frame
    frame1 = cap.read()

    # reduce size
    frame1 = imutils.resize(frame1, width=320)

    # ret, frame1 = cap.read()
    # Grayscale
    prev = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)

    hsv = np.zeros_like(frame1)
    # We fix saturation into the maximal possible value
    hsv[...,1] = 255

    # create_iteration number
    iter_number = 0

    while(1):
        # get timestamp
        timestamp = datetime.datetime.now().isoformat(" ")
        frame2 = cap.read()
        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if frame2 is None:
            print("End of video. Getting out")
            break

        # reduce the frame so that we speed up computation
        frame2 = imutils.resize(frame2, width=320)

        gray = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
    # see docs here: https://docs.opencv.org/2.4/modules/video/doc/motion_analysis_and_object_tracking.html
        flow = cv2.calcOpticalFlowFarneback(prev, gray, None,
         pyr_scale = 0.5,
         levels = 3,
         winsize = 20, # averaging window size; larger values increase the algorithm robustness to image noise and give more chances for fast motion detection, but yield more blurred motion field.
         iterations = 3,
         poly_n = 5, # typically poly_n =5 or 7.
         poly_sigma = 1.1, # 1.1 for poly_n = 5 and 1.5 for poly_n = 7
         flags = 0)    

        # For OpenCV’s implementation, it computes the magnitude and direction
        # of optical flow from a 2-channel array of flow vectors (dx/dt,dy/dt),
        # the optical flow problem. 
        # It then visualizes the angle (direction) of flow by hue and the distance (magnitude)
        # of flow by value of HSV color representation. 
        mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])

        # Increase signal to noise ratio ? 
        # We can always do this afterwards but visual normalization might need it
        #mag = mag * mag
        # np.median is probably less noisy but it misses a lot of movement
        mag_deque.append(np.sum(mag))

        # Direction/angle goes into hue (first channel)
        hsv[...,0] = ang*180/np.pi/2
        # magnitude goes into value (third channel)
        # We normalize to be able to see...math for data will use the mag object  
        hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
        bgr = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)    

        #bgr_blur = cv2.medianBlur(bgr, 5)
        #bgr_blur[bgr_blur < 50]  = 0    

       
        cv2.putText(bgr, "total mov: " + str(round(np.sum(mag),2)), 
            (10, 20), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1,
            (255,255,255),
            1)    

        if (show_video):
            cv2.imshow('frame2',bgr)
            cv2.imshow('original', gray)
            #cv2.imshow('blurr', bgr_blur)    

            k = cv2.waitKey(1) & 0xff
            if k == 27:
                break
            elif k == ord('s'):
                with open('mag_deque.csv','a') as outfile:
                    np.savetxt(outfile, mag_deque,
                    delimiter=',', fmt='%s')
        else:
            # if we don't give any feedback it's difficult to know
            print("opt_flow.py Iteration: " + str(iter_number) + " " +
             "Total movement: " + str(np.sum(mag)),
              end = "\r")

        # Clean-up
        # assign the last frame to previous
        prev = gray
        unsaved_elements = iter_number % maxlen
        if (unsaved_elements == 0):
            save_deque(iter_number, timestamp, mag_deque, maxlen, filename)
        iter_number = iter_number + 1

    exit_handler(iter_number, timestamp, mag_deque, maxlen, filename)
    return mag_deque


if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-source", "--source", required=True,
    help="'webcam' or path to video")
    ap.add_argument("-show_video", "--show_video", 
        required=False, default = True,
        # this is needed for transforming str to bool
        type=lambda x: (str(x).lower() == 'true'),
        help="Boolean, whether to show the video while computing flow (default is True)")
    args = vars(ap.parse_args())
    if args["source"] == "webcam":
        # we are using the webcam 0...might create problems
        cap = imutils.video.VideoStream(src=0).start()
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + "_opt_flow.csv"
        opt_flow(cap, show_video = args["show_video"], filename = filename)
    else:
        # all hell can break lose here but whatever
        cap = imutils.video.FileVideoStream(args["source"]).start()
        base = os.path.splitext(os.path.basename(args["source"]))[0]
        filename =  base + "_opt_flow.csv"
        opt_flow(cap, show_video = args["show_video"], filename = filename)