# This script will create a cron job for calling git pull automatically

from crontab import CronTab
# this is what we want to run
cmd_command = "cd ~/homecage_quantification/ && git pull"

job_comment = 'automatic git pull'

# get cron object
cron = CronTab(user="pi")
# don't create a new job if it is already there
# first check if it's already there

job_exists = any(list(map(lambda x: x.comment == job_comment, cron)))

if job_exists:
    for job in cron:
        if job.comment == job_comment:
            print("job named: " + job_comment + " already exists, scheduling 2 hours")
            job.hour.every(2)
            # write the program
            cron.write()
else:
    # only here, create it
    # create a new job
    job = cron.new(command = cmd_command, comment=job_comment)
    # schedule it every minute
    job.hour.every(2)
    # write the program
    cron.write()

print("Current cron tab (same as $ crontab -l)")
print("--------------------------------------")
print(cron)