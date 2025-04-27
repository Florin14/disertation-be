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
from project_helpers.responses import ErrorResponse
from .router import router
from ..models import SchedulerBody, SchedulerResponse
from project_helpers.error import Error
from .helpers import add_new_job
from extensions import scheduler


@router.put("/{jobId}", response_model=SchedulerResponse)
async def update_scheduler(jobId: str, body: SchedulerBody):
    scheduler.remove_job(jobId, jobstore="manual_jobs")
    job = add_new_job(body, jobId=jobId)
    if job:
        return SchedulerResponse.from_job(job)
    return ErrorResponse(error=Error.JOB_FUNCTION_NOT_FOUND)
