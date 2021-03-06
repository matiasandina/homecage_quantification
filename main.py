import cv2
import sys
from flask import Flask, render_template, Response
from camera import VideoCamera
from flask_basicauth import BasicAuth
import time
import threading
from opt_flow import opt_flow
import datetime
import socket
import os

# source
# https://github.com/HackerShackOfficial/Smart-Security-Camera

# Modified Matias Andina 2020-02-01

# creates a camera object, don't flip vertically
# we will not use this camera to record
video_camera = VideoCamera(
	flip = False, 
	usePiCamera = False, 
	resolution = (640, 480),
	record = False,
	record_timestamp = True
	) 

# App Globals (do not edit)
app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'choilab'
app.config['BASIC_AUTH_PASSWORD'] = 'choilab'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

def running_flag():
	# caution this only works for raspberry PIs on WiFI
	mac = open('/sys/class/net/wlan0/address').readline()
	# replace "\n" coming from readline()
	mac = mac.replace("\n", "")

	while True:
		with open('/home/pi/homecage_quantification/running.txt', "w") as the_file:
			# because we are using .utcnow() 
			# dates will be given as UTC (hence you need to transform to your local time)
			the_file.write(datetime.datetime.utcnow().isoformat())
		# send IP to choilab
		cmd_command = "scp ~/homecage_quantification/running.txt choilab@10.93.6.88:~/raspberry_IP/" + mac
		os.system(cmd_command)
		# sleep 1 minutes
		time.sleep(1 * 60)


def calculate_flow():
	# give the video camera, don't show the feed
	# opt_flow already has a while loop
	# opt_flow handles saving data
	filename = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "_opt_flow.csv"
	movement = opt_flow(video_camera, True, filename = filename)

def get_ip_address(remote_server="google.com"):
	"""
	Return the/a network-facing IP number for this system.
	"""
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
		s.connect((remote_server, 80))
		return s.getsockname()[0]

@app.route('/')
@basic_auth.required
def index():
    return render_template('index.html')

def gen(camera):
    camera_stamp = get_ip_address()
    while True:
    	# frame will be contaminated with timestamp and ip address
    	# we accept this as noise on opt_flow
        frame = camera.get_frame(label_time=True, camera_stamp = camera_stamp)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # start the opt_flow program
    t = threading.Thread(target=calculate_flow, args=())
    t.daemon = True
    t.start()
    # make a flag to save a small file with the date
    # this will be read by central computer 
    running_flag = threading.Thread(target=running_flag, args=())
    running_flag.daemon = True
    running_flag.start()
    # start the app streaming 
    print("To see feed connect to " + get_ip_address() + ":5000")
    # to do, read ifconfig and assign IP using raspberry's IP
    app.run(host='0.0.0.0', port = 5000, debug=False)
