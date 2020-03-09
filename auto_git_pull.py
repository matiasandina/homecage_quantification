# This script will create a cron job for calling git pull automatically

from crontab import CronTab
# this is what we want to run
cmd_command = "cd ~/homecage_quantification/ && git pull"

cron = CronTab(user="pi")
# create a new job
job = cron.new(command = cmd_command, comment='automatic git pull')
# schedule it 
job.hour.every(2)
# write the program
cron.write()