# This script will send ip txt file

# first call python to make the file
# (could be done in bash but :shrug:)

python3 ~/homecage_quantification/get_ip.py

IFACE=wlan0
read MAC </sys/class/net/$IFACE/address

# log in and make dir if needed
ssh choilab@10.93.3.88 mkdir -p raspberry_IP/$MAC 


a="_ip.txt"

scp ~/homecage_quantification/$MAC$a choilab@10.93.3.88:~/raspberry_IP/$MAC
