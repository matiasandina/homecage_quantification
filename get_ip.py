# This script will save a file with the ip on boot
# to setup this to run on boot do
# (this is accomplished on setup.sh on /homecage_quantification)


import subprocess
import re
import time
import socket

# This fails when implemented from cron
# Kept for record of perfectly functional code that crashes with cron!
#def get_ip():
#    # this will get the wlan0 ip
#    # good for Linux, probably not for other OS
#    cmd_call = "ifconfig wlan0 | awk '/inet /{print $2}'"
#
#    p = subprocess.Popen(cmd_call, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#    # read lines should give a list with one element
#    ip = p.stdout.readlines()
#    # take first element and decode (removes the 'b) 
#    ip = ip[0].decode('utf-8')
#
#    # find the numbers
#    numbers = re.findall('[0-9]+', ip)
#    # join them with colons
#    clean_ip = ':'.join(numbers)
#    return(clean_ip)


def get_ip(remote_server="google.com"):
    """
    Return the/a network-facing IP number for this system.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
        s.connect((remote_server, 80))
        return s.getsockname()[0]

def get_mac(interface = 'wlan0'):
    # This is good for Raspberry PIs, not good for other OS !
    # possible interfaces ['wlan0', 'eth0']
    try:
        mac = open('/sys/class/net/'+interface+'/address').readline()
    except:
        mac = "00:00:00:00:00:00"

    return mac[0:17]

### main -----
# let's sleep for a while until we can make sure we have an ip
#sleep_time =300 #seconds
#print("sleeping for " + str(sleep_time) + " seconds")
#time.sleep(sleep_time)
print("get_ip.py is retrieving MAC & IP")

# IP retrieval too soon might fail with IP = 1
ip = get_ip()
mac = get_mac()

# Save to file
folder = "homecage_quantification/"

file = open(folder + mac + "_ip.txt", "w") 
file.write("MAC address is: "+ mac + "\n")
file.write("IP is: " + ip)
file.close() 