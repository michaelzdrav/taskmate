import time
import atexit

def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))

def start_scheduler(scheduler):
    scheduler.add_job(func=print_date_time, trigger="interval", seconds=60)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

