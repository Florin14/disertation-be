from project_helpers.responses import ConfirmationResponse
from .router import router
from extensions import scheduler


@router.delete("", response_model=ConfirmationResponse)
async def delete_all_schedulers():
    scheduler.remove_all_jobs(jobstore="manual_jobs")
    return ConfirmationResponse()
