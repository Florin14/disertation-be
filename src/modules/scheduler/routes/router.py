
from fastapi import APIRouter, Depends
from constants import PlatformRoles
from project_helpers.dependencies import JwtRequired

router = APIRouter(
    prefix="/schedulers", tags=["Scheduler"], dependencies=[Depends(JwtRequired(roles=[PlatformRoles.ADMIN]))]
)
