from project_helpers.responses import ConfirmationResponse
from .router import router
from extensions import scheduler


@router.delete("/{jobId}", response_model=ConfirmationResponse)
async def delete_scheduler(jobId: str):
    scheduler.remove_job(job_id=jobId, jobstore="manual_jobs")
    return ConfirmationResponse()
