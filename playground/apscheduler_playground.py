from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler

scheduler = BackgroundScheduler()

def simplest_func():
    print("This will keep working...")

scheduler.add_job(simplest_func, 'interval', seconds=2)

try:
    scheduler.print_jobs()
    scheduler.start()
except KeyboardInterrupt:
    pass

scheduler.print_jobs()

input("Press Enter to continue...")
