# This file is intended to make the install of dependencies easy on a fresh raspberri pi 4

# config git globals
git config --global user.name matiasandina
git config --global user.email matiasandina@gmail.com

# update
sudo apt-get update -y
sudo apt-get upgrade -y

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



