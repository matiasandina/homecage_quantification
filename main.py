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

# source
# https://github.com/HackerShackOfficial/Smart-Security-Camera

# Modified Matias Andina 2020-02-01

# creates a camera object, don't flip vertically
video_camera = VideoCamera(
	flip = False, 
	usePiCamera = False, 
	resolution = (640, 480),
	record = True
	) 

# App Globals (do not edit)
app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'choilab'
app.config['BASIC_AUTH_PASSWORD'] = 'choilab'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)


def calculate_flow():
	# give the video camera, don't show the feed
	# opt_flow already has a while loop
	# opt_flow handles saving data
	movement = opt_flow(video_camera, False)

	# TODO: add device info here


def get_ip_address(remote_server="google.com"):
	"""
	Return the/a network-facing IP number for this system.
	"""
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
		s.connect((remote_server, 80))
		return s.getsockname()[0]

# def config_raspberry():
	# TODO
	# ifconfig
	# modify html template

@app.route('/')
@basic_auth.required
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame(label_time=True)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    t = threading.Thread(target=calculate_flow, args=())
    t.daemon = True
    t.start()
    print("To see feed connect to " + get_ip_address() + ":5000")
    # to do, read ifconfig and assign IP using raspberry's IP
    app.run(host='0.0.0.0', port = 5000, debug=False)
