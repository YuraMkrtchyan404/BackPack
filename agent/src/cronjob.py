from crontab import CronTab
import getpass

def get_cron_format(backup_frequency):
    parts = backup_frequency.split()
    
    if len(parts) > 2:
        raise ValueError("Invalid frequency format")
    
    if len(parts) == 1:
        frequencies = {
            'minutely': '* * * * *',
            'hourly': '0 * * * *',
            'daily': '0 0 * * *',
            'weekly': '0 0 * * 0',
            'monthly': '0 0 1 * *',
            'boot': '@reboot'
        }
        if parts[0] not in frequencies:
            raise ValueError(f"Unsupported frequency: '{parts[0]}'.")
        return frequencies[parts[0]]
    elif len(parts) == 2:
        frequency, interval = parts[0], parts[1]
        try:
            interval = int(interval)
        except ValueError:
            raise ValueError("Interval must be a valid integer.")

        interval_expressions = {
            'minutely': f"*/{interval} * * * *",
            'hourly': f"0 */{interval} * * *",
            'daily': f"0 0 */{interval} * *",
            'monthly': f"0 0 1/{interval} * *",
            'weekly': f"0 0 * * */{interval}"
        }

        if frequency not in interval_expressions:
            raise ValueError(f"Unsupported frequency with interval: '{frequency}'.")

        return interval_expressions[frequency]

    else:
        raise ValueError("Incorrect frequency or interval format.")

def setup_cron_job(command, backup_frequency):
    cron = CronTab(user=getpass.getuser())
    cron.remove_all(comment='snapshot_job') #TODO this comment is used to delete cron jobs with the same comment (need to configure this any way)
    job = cron.new(command=command, comment='snapshot_job')
    cron_format = get_cron_format(backup_frequency)
    job.setall(cron_format)
    job.set_command(command)
    cron.write()
    print(f"Cron job set for {backup_frequency}: {job}")