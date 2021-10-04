import sensor, image, time, pyb
from pyb import USB_VCP
import os

def year(datetime):
    return str(datetime[0])
def month(datetime):
    return str('%02d' % datetime[1])
def day(datetime):
    return str('%02d' % datetime[2])
def hour(datetime):
    return str('%02d' % datetime[4])
def minute(datetime):
    return str('%02d' % datetime[5])
def second(datetime):
    return str('%02d' % datetime[6])
def timestamp(datetime):
    date_string = '-'.join([year(datetime), month(datetime), day(datetime)])
    time_string = '-'.join([hour(datetime), minute(datetime), second(datetime)])
    return "T".join([date_string, time_string])

def blink(led_number, sleep_time = 300):
    pyb.LED(led_number).on()
    pyb.delay(sleep_time)
    pyb.LED(led_number).off()
    pyb.delay(sleep_time)


def parse_date(data):
    # date will come in a string with (datetime object)"
    data = data.replace("(", "")
    data = data.replace(")", "")
    # split using the comma and transform the string into integers
    timestamp = [int(x) for x in data.split(",")]
    # the idea is to return a tupple we could give to the rtc
    timestamp = tuple(timestamp)
    return (timestamp)

def write_binary_time(string):
    # mind that the string will be binary, hence "wb"
    # mind the '/', without it it will write to the PC instead of the openmv SD card
    f=open('/binary_time.txt','wb')
    f.write(string)
    f.close()

def write__time(string):
    # mind the '/', without it it will write to the PC instead of the openmv SD card
    f=open('/time.txt','w')
    f.write(string)
    f.close()

def make_dir(name):
    try:
        os.mkdir("/" + name)
    except:
        print("Directory exists")
def date(datetime):
    return '-'.join([year(datetime), month(datetime), day(datetime)])
def create_filename(datetime, ext=".jpg"):
    rec_date = date(datetime)
    rec_hour = hour(datetime)
    make_dir("/" + rec_date)
    make_dir("/" + rec_date + "/" + rec_hour)
    filename = "/" + rec_date +  "/" + rec_hour "/" + timestamp(datetime)
    filename = filename + "_capture" + ext
    print(filename)
    return filename

# micropython does not have decode, this is a hack
def decode(binary_string):
    return "".join([chr(char) for char in binary_string])

rtc = pyb.RTC()
usb = USB_VCP()

# Blink blue at start
blink(3)
pyb.delay(500)
blink(3)

## Now we enter Lepton Territory

import sensor, image, time, math

# Color Tracking Thresholds (Grayscale Min, Grayscale Max)
threshold_list = [(220, 255)]

# Set the target temp range here
min_temp_in_celsius = 25
max_temp_in_celsius = 42

to_write = str(min_temp_in_celsius) + " " + str(max_temp_in_celsius)

# write the parameters we are using to file
txt = create_filename(rtc.datetime(), ext=".txt")
gg=open(txt,'w')
gg.write(to_write)
gg.close()



print("Resetting Lepton...")
# These settings are applied on reset
sensor.reset()
sensor.ioctl(sensor.IOCTL_LEPTON_SET_MEASUREMENT_MODE, True)
sensor.ioctl(sensor.IOCTL_LEPTON_SET_MEASUREMENT_RANGE, min_temp_in_celsius, max_temp_in_celsius)
print("Lepton Res (%dx%d)" % (sensor.ioctl(sensor.IOCTL_LEPTON_GET_WIDTH),
                              sensor.ioctl(sensor.IOCTL_LEPTON_GET_HEIGHT)))
print("Radiometry Available: " + ("Yes" if sensor.ioctl(sensor.IOCTL_LEPTON_GET_RADIOMETRY) else "No"))

sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=5000)

pyb.LED(1).on()
while(True):
    data = usb.read()
    if data != None:
        if len(data) >= 4:
            # we want to check that starts with date and last element is ")"
            if data[:4] == b'date':
                pyb.LED(1).off()
                # now we parse the time
                time_stamp = data[5:]
                write_binary_time(time_stamp)
                # now decode into string
                time_stamp = decode(time_stamp)
                # and transform to tuple
                tuple_time = parse_date(time_stamp)
                # set the clock!
                rtc.datetime(tuple_time)
                try:
                    # generate filename with stamp
                    filename = create_filename(rtc.datetime())
                    # take the pic
                    img = sensor.snapshot()
                    # save the pic
                    img.save(filename)
                    # blink RED LED to give user feedback
                    blink_times = 5
                    for i in range(blink_times):
                        blink(1, sleep_time=500)

                except:
                    # do something here to tell me we couldn't take one picture
                    f=open('/error.txt','w')
                    string = "Error happened at: " + timestamp(rtc.datetime())
                    f.write(string)
                    f.close()
                    pass
        else:
            # TODO: introduce delay here ? this while is cycling very fast 
            # maybe we should add pyb.delay(10)
            # if data[:4] == "stop"
            # machine.reset() ?
            # else continue
            continue
    else:
        continue

