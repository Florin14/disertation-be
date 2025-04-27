# Id: jwt_required.py 202307 12/07/2023
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


class GetCurrentUser:
    def __init__(self, userModel):
        self.userModel = userModel

    def __call__(self, auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
        claims = auth.get_raw_jwt()
        return db.query(self.userModel).get(claims.get("userId"))
