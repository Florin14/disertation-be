# Id: helpers.py 202307 19/07/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202307
#   Date: 19/07/2023
#
# License description...
import uuid
from pytz import timezone
from extensions import scheduler
from ..models import SchedulerBody
from jobs.manual_start import *


def add_new_job(body: SchedulerBody, jobId=str(uuid.uuid4())):
    jobFunction = globals().get(body.jobName)
    if jobFunction is not None and callable(jobFunction):
        if body.trigger == "cron":
            return scheduler.add_job(
                jobFunction,
                day_of_week=body.dayOfWeek,
                jobstore="manual_jobs",
                trigger=body.trigger,
                timezone=timezone(body.timezone),
                hour=body.hour,
                start_date=body.startDate,
                end_date=body.endDate,
                minute=body.minute,
                name=body.jobName,
                id=jobId,
            )
        else:
            return scheduler.add_job(
                jobFunction,
                jobstore="manual_jobs",
                trigger=body.trigger,
                start_date=body.startDate,
                end_date=body.endDate,
                **{body.frequencyUnit: body.frequencyValue},
                name=body.jobName,
                id=jobId
            )
    return None
