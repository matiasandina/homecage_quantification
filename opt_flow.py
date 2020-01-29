import cv2
import numpy as np
import imutils
import argparse
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from collections import deque

def opt_flow(cap, show_video):

    mag_deque = deque(maxlen=10000)

    # reduce fps
    #cap.set(cv2.CAP_PROP_FPS, 15)

    # grab the current frame
    frame1 = cap.read()

    # handle the frame from VideoCapture or VideoStream
    # frame1 = frame[1] if args.get("video", False) else frame1
    # reduce size
    frame1 = imutils.resize(frame1, width=320)

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame1 is None:
        print("End of video. Exit")
        return

    # ret, frame1 = cap.read()
    # Grayscale
    prev = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)

    hsv = np.zeros_like(frame1)
    # We fix saturation into the maximal possible value
    hsv[...,1] = 255
    while(1):
        frame2 = cap.read()
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
                with open('mag_deque.csv','w') as outfile:
                    np.savetxt(outfile, mag_deque,
                    delimiter=',', fmt='%s')
        # assign the last frame to 
        prev = gray    

#    cap.release()
    cv2.destroyAllWindows()
    # return mag_deque
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
        # we are using the webcam 0
        cap = imutils.video.VideoStream(src=0).start()
        opt_flow(cap, show_video = args["show_video"])
    else:
        # all hell can break lose here but whatever
        cap = imutils.video.FileVideoStream(args["source"]).start()
        opt_flow(cap, show_video = args["show_video"])