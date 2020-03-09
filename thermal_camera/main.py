import sensor, image, time, pyb
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
def create_filename(datetime, ext=".jpg"):
    return timestamp(datetime) + "_capture" + ext
def blink(led_number, sleep_time = 300):
    pyb.LED(led_number).on()
    pyb.delay(sleep_time)
    pyb.LED(led_number).off()

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


# micropython does not have decode, this is a hack
def decode(binary_string):
    return "".join([chr(char) for char in binary_string])


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
clock = time.clock()
rtc = pyb.RTC()
from pyb import USB_VCP
usb = USB_VCP()

blink(3)
pyb.delay(500)
blink(3)

# Get time from raspberry

while(True):
    pyb.LED(3).on()
    clock.tick()
    data = usb.read()
    if data != None:
        if len(data) >= 4:
            # we want to check that starts with date and last element is ")"
            if data[:4] == b'date':
                pyb.LED(3).off()
                # now we parse the time
                time_stamp = data[5:]
                write_binary_time(time_stamp)
                # now decode into string
                time_stamp = decode(time_stamp)
                # and transform to tuple
                tuple_time = parse_date(time_stamp)
                # set the clock!
                rtc.datetime(tuple_time)
                blink(2)
                pyb.delay(500)
                blink(2)
                # we set the clock properly, then break!
                break
        else:
            continue
    else:
        continue


while(True):
    # capture lepton
    # filename = create_filename(rtc.datetime())
    # img.save(filename)

