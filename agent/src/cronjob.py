from crontab import CronTab
import getpass

def get_cron_format(backup_frequency):
    """ Translate friendly backup_frequency terms to cron format strings. """
    return {
        'minutely': '* * * * *',
        'hourly': '0 * * * *',
        'daily': '0 0 * * *',
        'weekly': '0 0 * * 0',
        'monthly': '0 0 1 * *',
        'yearly': '0 0 1 1 *',
        'boot': '@reboot'
    }.get(backup_frequency, '* * * * *')  

def setup_cron_job(command, backup_frequency):
    cron = CronTab(user=getpass.getuser())
    cron.remove_all(comment='snapshot_job')
    job = cron.new(command=command, comment='snapshot_job')
    job.setall(get_cron_format(backup_frequency))
    job.set_command(f"{command}")
    cron.write()
    print(f"Cron job set for {backup_frequency}: {job}")