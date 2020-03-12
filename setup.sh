# This file is intended to make the install of dependencies easy on a fresh raspberri pi 4

# config git globals
git config --global user.name matiasandina
git config --global user.email matiasandina@gmail.com

# update
sudo apt-get update -y
sudo apt-get upgrade -y

# setup the screen resolution on config.txt
sudo sh -c "echo 'hdmi_force_hotplug=1' >> /boot/config.txt"
sudo sh -c "echo 'hdmi_group=2' >> /boot/config.txt"
sudo sh -c "echo 'hdmi_mode=82' >> /boot/config.txt"


# install requirements for opencv
sudo apt-get install libhdf5-dev -y
sudo apt-get install libatlas-base-dev -y
sudo apt-get install libjasper-dev -y
sudo apt install libqtgui4 -y
sudo apt-get install libqt4-test -y

# Install python garbage
sudo pip3 install numpy
sudo pip3 install pandas
# Install opencv specific version see: https://github.com/piwheels/packages/issues/59
sudo pip3 install opencv-contrib-python==4.1.0.25
sudo pip3 install matplotlib
sudo pip3 install imutils
sudo pip3 install python-crontab
sudo pip3 install flask_basicauth

# setup the ssh keys
bash setup_ssh.sh

# setup sending ip on startup
# for this we use cron_setup.py script
# this script will call send_ip.sh on every reboot
python3 ~/homecage_quantification/setup_cron.py


# setup scheduling git pulls
# for this, we use auto_git_pull.py script
python3 ~/homecage_quantification/auto_git_pull.py
