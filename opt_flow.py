import cv2
import numpy as np
import imutils
import argparse
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from collections import deque
import datetime
import os

def exit_handler(iter_number, timestamp_deque, mag_deque, xy, maxlen, filename):
    print('Application is ending')
    print('Calling save_deque()')
    # save all deques
    save_deque(iter_number, timestamp_deque, mag_deque, xy, maxlen, filename) 
    cv2.destroyAllWindows()


def save_deque(iter_number, timestamp_deque, deque_to_save, xy, maxlen, filename):

    # iter_number[-1] is the last iteration if deque... here iternumber is an int
    # we could also do max(iter_number)

    unsaved_elements = iter_number % maxlen
    
    if (unsaved_elements == 0):
        print("Saving " + filename + " on iteration..." + str(iter_number))
        # array with timestamp and deque to save, transpose for having them as cols
        d = np.array([timestamp_deque, deque_to_save, xy]).T
        with open(filename,'a') as outfile:
            np.savetxt(outfile, d,
            delimiter=',', fmt='%s')

    else:
        # convert to list and slice the last unsaved elements
        print("Saving rest of " + filename )
        timestamp_rest = list(timestamp_deque)[-unsaved_elements:]
        rest = list(deque_to_save)[-unsaved_elements:]
        xy_rest = list(xy)[-unsaved_elements:]
        d_rest = np.array([timestamp_rest, rest, xy_rest]).T
        # Here we only save the rest 
        with open(filename,'a') as outfile:
            np.savetxt(outfile, d_rest,
            delimiter=',', fmt='%s')
    return


def get_centroid(mask):
    kernel = np.ones((5, 5), np.uint8)
    # Do some erosion-dilation to clear noise
    mask = cv2.erode(mask, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # Fill holes inside of mask, we will close them
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(),
                            cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    # This is a function that checks the length of contours
    # it is related to the opencv version we are using

    cnts = imutils.grab_contours(cnts)

    # mouse center
    if len(cnts)>0:
        c = max(cnts, key=cv2.contourArea)
        # ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        mouse_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        return mouse_center
    else:
        return None

def opt_flow(cap, show_video, filename):
    # buffer size for keeping RAM smooth 
    maxlen = 1000
    mag_deque = deque(maxlen=maxlen)
    timestamp_deque = deque(maxlen=maxlen)
    xy_deque = deque(maxlen=maxlen)

    # grab the current frame
    frame1 = cap.read()
    # images will come as
    # (h, w, channels)
    original_width = frame1.shape[1]
    # resize_width for ease of computation
    resize_width = 320

    # reduce size
    frame1 = imutils.resize(frame1, width=resize_width)

    # ret, frame1 = cap.read()
    # Grayscale
    prev = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)

    hsv = np.zeros_like(frame1)
    # We fix saturation into the maximal possible value
    hsv[...,1] = 255

    # create_iteration number
    iter_number = 0

    while(True):
        # get timestamp
        timestamp = datetime.datetime.now().isoformat(" ")
        timestamp_deque.append(timestamp)
        frame2 = cap.read()
        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if frame2 is None:
            print("End of video. Getting out")
            break

        # reduce the frame so that we speed up computation
        frame2 = imutils.resize(frame2, width=resize_width)

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
        sum_mag = np.sum(mag)
        mag_deque.append(sum_mag)

        # if there's enough movement
        if sum_mag > 1000:        
           # if mag is 1 for any pixel looks like real movement
           # try to calculate mask and centroid
           # calculate the mask as cv2 likes it
           mask = np.array((mag>1)*255).astype('uint8')
           xy = get_centroid(mask)
           # xy will be a tupple
           # we need to adjust with resize factor
           # the way to keep it tupple is with tuple and list comprehension
           if xy is not None:
               xy = tuple([int(value * original_width/resize_width) for value in xy])
           xy_deque.append(xy)
        else:
            xy_deque.append(None)
            mask = None


        if (show_video):
            # Direction/angle goes into hue (first channel)
            hsv[...,0] = ang*180/np.pi/2
            # magnitude goes into value (third channel)
            # We normalize to be able to see...
            # Because this distorts values, all data analysis will use the mag object  
            hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
            bgr = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)    
            
            #bgr_blur = cv2.medianBlur(bgr, 5)
            #bgr_blur[bgr_blur < 50]  = 0 
            # put text for the total movement
            cv2.putText(bgr, "total mov: " + str(round(sum_mag,2)), 
            (10, 20), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1,
            (255,255,255),
            1)    
            cv2.imshow('frame2',bgr)
            cv2.imshow('original', gray)
            #cv2.imshow('blurr', bgr_blur)
            if mask is not None:
                show_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                if xy is not None:
                    # we need to correct back for the resizing to show
                    xy_show = tuple([int(value * resize_width/original_width) for value in xy])
                    cv2.circle(show_mask, xy_show,
                       5,  # a very small circle
                       (0, 0, 255),  # red
                       -1)  # Negative thickness means that a filled circle is to be drawn.
                cv2.imshow('mask', show_mask)


            k = cv2.waitKey(1) & 0xff
            if k == 27:
                break
            # possiblilty to save via command
            #elif k == ord('s'):
            #    with open('mag_deque.csv','a') as outfile:
            #        np.savetxt(outfile, mag_deque,
            #        delimiter=',', fmt='%s')
        else:
            # if we don't give any feedback it's difficult to know
            print('opt_flow.py Iteration: {} Total movement: {}'.format(iter_number, sum_mag),
              end = "\r")

        # Clean-up
        # assign the last frame to previous
        prev = gray
        unsaved_elements = iter_number % maxlen
        if (unsaved_elements == 0):
            save_deque(iter_number, timestamp_deque, mag_deque, xy_deque, maxlen, filename)
        iter_number = iter_number + 1

    exit_handler(iter_number, timestamp_deque, mag_deque, xy_deque, maxlen, filename)
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
        filename = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "_opt_flow.csv"
        # make path absolute
        filename = os.path.join("/home/pi/homecage_quantification", filename)
        opt_flow(cap, show_video = args["show_video"], filename = filename)
    else:
        # all hell can break lose here but whatever
        cap = imutils.video.FileVideoStream(args["source"]).start()
        base = os.path.splitext(os.path.basename(args["source"]))[0]
        filename =  base + "_opt_flow.csv"
        opt_flow(cap, show_video = args["show_video"], filename = filename)