import os
# -----------------------------------------------
# CAUTION ####
# THIS WILL PERMANENTLY REMOVE THINGS
# DO NOT RUN UNLESS YOU HAVE COPIES OF YOUR DATA
# -----------------------------------------------

# Thermal Cameras ------
# This will remove things that start with 20 (as in 2020 and the next 80 years) 
# it will not clean EVERYTHING, but close enough
os.system("/media/pi/*/20* -exec rm -f {} +")
# now the directories 
os.system("/media/pi/*/20* -exec rm -f {} +")

# Color Cameras -----
# limit search to maxdepth 1, so that we only look on homecage_quantification folder
os.system("find /home/pi/homecage_quantification/ -maxdepth 1 -name '*_opt_flow.csv' -type f -exec rm -f {} +")
os.system("find /home/pi/homecage_quantification/ -maxdepth 1 -name '*config.csv' -type f -exec rm -f {} +")