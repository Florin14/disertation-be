# Id: router.py 202305 11/05/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202305
#   Date: 11/05/2023
#
# License description...
from fastapi import APIRouter, Depends
from constants import PlatformRoles
from project_helpers.dependencies import JwtRequired

router = APIRouter(
    prefix="/schedulers", tags=["Scheduler"], dependencies=[Depends(JwtRequired(roles=[PlatformRoles.ADMIN]))]
)
