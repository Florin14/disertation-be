# Id: router.py 202307 05/07/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202307
#   Date: 05/07/2023
#
# License description...
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authentication"])
