# Id: logout.py 202307 12/07/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202307
#   Date: 12/07/2023
#
# License description...
from fastapi import Depends
from extensions.auth_jwt import AuthJWT
from sqlalchemy.orm import Session
from extensions import get_db
from project_helpers.responses import ConfirmationResponse
from .router import router
from ..models import BlacklistModel


@router.post("/logout", response_model=ConfirmationResponse)
def logout(auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
    auth.jwt_required()
    rawData = auth.get_raw_jwt()
    blackList = BlacklistModel(exp=rawData.get("exp"), token=rawData.get("jti"))
    db.add(blackList)
    db.commit()
    auth.unset_jwt_cookies()
    return ConfirmationResponse()
