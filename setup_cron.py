from crontab import CronTab
# this is what we want to run
cmd_command = "bash ~/homecage_quantification/send_ip.sh"

cron = CronTab(user="pi")
# create a new job
job = cron.new(command = cmd_command, comment='send ip to choilab1')
# schedule it every reboot
job.every_reboot()
# write the program
cron.write()