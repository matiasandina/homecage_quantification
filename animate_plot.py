import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
plt.style.use('seaborn-pastel')
import pandas as pd
import cv2
import imutils
from imutils.video import FileVideoStream
import time

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


df = pd.read_csv('mag_deque.csv', header = None)
df = np.array(df)
# accumulate distance
#df = np.cumsum(df)

# camera
cap = FileVideoStream("Trial1.mpg").start()

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
