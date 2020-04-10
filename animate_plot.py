import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
plt.style.use('seaborn-pastel')
import pandas as pd
import cv2
import imutils
from imutils.video import FileVideoStream
import time
import argparse

def grab_frame(cap):
    frame = cap.read()
    frame = imutils.resize(frame, width=320)
    return cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

def init():
    ax1.set_xlim(0, 10000)
    ax1.set_ylim(0, 4 *10e3)
    return ln, im2

def update(frame):
    xdata.append(frame)
    ydata.append(df[frame])
    ln.set_data(xdata, ydata)
    im2.set_data(grab_frame(cap))
    time.sleep(1/30)
    ax1.set_xlim(frame - 200, frame + 100)
    return ln, im2

# things to run from command line
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-video", "--video", required=True,
    help="path to video")
    ap.add_argument("-data", "--data", 
        required=True, 
        help="path to data")
    args = vars(ap.parse_args())

    
    df = pd.read_csv(args["data"])
    # rename the opt_flow output to have second column named flow
    # will fail if you don't do this manually
    df = np.array(df["flow"])
    # accumulate distance
    #df = np.cumsum(df)

    # camera
    cap = FileVideoStream(args["video"]).start()

    # fig, ax = plt.subplots()
    xdata, ydata = [], []


    #create two subplots
    ax1 = plt.subplot(2,1,1)
    ln, = plt.plot([], [], color=(0,0,1))

    #create two image plots
    ax2 = plt.subplot(2,1,2)
    im2 = ax2.imshow(grab_frame(cap))



    ani = FuncAnimation(plt.gcf(), update, interval=1,
                        init_func=init, blit=False)

    plt.show()

