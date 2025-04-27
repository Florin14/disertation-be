from .router import router
from ..models import SchedulerResponse
from extensions import scheduler


@router.get("/{jobId}", response_model=SchedulerResponse)
async def get_scheduler(jobId: str):
    scheduler._lookup_job(job_id=jobId, jobstore_alias="manual_jobs")
    job = scheduler.get_job(jobId, jobstore="manual_jobs")
    return SchedulerResponse.from_job(job)
