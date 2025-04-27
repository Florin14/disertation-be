import logging
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

scheduler = BackgroundScheduler(logger=logging.getLogger(), daemon=True, timezone=timezone("Europe/Bucharest"))


def init_scheduler(engine, starter_callback=None):
    global scheduler
    autoJobStore = SQLAlchemyJobStore(engine=engine, tablename="auto_jobs")
    manualJobStore = SQLAlchemyJobStore(engine=engine, tablename="manual_jobs")
    scheduler.add_jobstore(autoJobStore, alias="auto_jobs")
    scheduler.add_jobstore(manualJobStore, alias="manual_jobs")
    scheduler.start()

    if starter_callback:
        starter_callback()
