# Id: add_scheduler.py 202307 18/07/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202307
#   Date: 18/07/2023
#
# License description...
from typing import List
from .router import router
from ..models import SchedulerResponse
from extensions import scheduler


@router.get("", response_model=List[SchedulerResponse])
async def fetch_schedulers():
    jobs = scheduler.get_jobs(jobstore="manual_jobs")
    return [SchedulerResponse.from_job(job) for job in jobs or []]
