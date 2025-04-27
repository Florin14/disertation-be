from typing import List
from .router import router
from ..models import SchedulerResponse
from extensions import scheduler


@router.get("", response_model=List[SchedulerResponse])
async def fetch_schedulers():
    jobs = scheduler.get_jobs(jobstore="manual_jobs")
    return [SchedulerResponse.from_job(job) for job in jobs or []]
