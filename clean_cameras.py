import os
# -----------------------------------------------
# CAUTION ####
# THIS WILL PERMANENTLY REMOVE THINGS
# DO NOT RUN UNLESS YOU HAVE COPIES OF YOUR DATA
# -----------------------------------------------

# Thermal Cameras ------
# this will remove every file except main.py
# it will also try to remove /media/pi/SD_card but give error because its busy
os.system("find /media/pi ! -name 'main.py' -type f -exec rm -f {} +")
# now the directories 
os.system("find /media/pi ! -name 'main.py' -type d -exec rm -f {} +")

# Color Cameras -----
os.system("find /home/pi/homecage_quantification/ -name '*_opt_flow.csv' -type f -exec rm -f {} +")
os.system("find /home/pi/homecage_quantification/ -name '*config.csv' -type f -exec rm -f {} +")