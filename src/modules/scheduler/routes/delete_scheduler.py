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
from project_helpers.responses import ConfirmationResponse
from .router import router
from extensions import scheduler


@router.delete("/{jobId}", response_model=ConfirmationResponse)
async def delete_scheduler(jobId: str):
    scheduler.remove_job(job_id=jobId, jobstore="manual_jobs")
    return ConfirmationResponse()
