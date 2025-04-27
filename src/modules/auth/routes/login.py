# Id: login.py 202307 05/07/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202307
#   Date: 05/07/2023
#
# License description...
from fastapi import Depends
from extensions.auth_jwt import AuthJWT
from sqlalchemy.orm import Session
from extensions import get_db
from .dependencies import VerifyRecaptcha
from project_helpers.error import Error
from project_helpers.functions import verify_password
from project_helpers.responses import ErrorResponse
from ..models import LoginBody, LoginResponse, LoginAttemptModel
from modules.employer.models.employer_model import EmployerModel
from modules.job.models.job_model import JobModel
from modules.employee.models.employee_model import EmployeeModel
from ...user import UserModel
from .router import router


@router.post("/login", response_model=LoginResponse, dependencies=[Depends(VerifyRecaptcha())])
def login(body: LoginBody, auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if user is None:
        user = db.query(EmployerModel).filter(EmployerModel.email == body.email).first()

    if user and verify_password(user.password, body.password):
        accessToken = auth.create_access_token(user.email, user_claims=user.getClaims())
        refreshToken = auth.create_refresh_token(user.email)
        # Set the JWT cookies in the response
        auth.set_access_cookies(accessToken)
        auth.set_refresh_cookies(refreshToken)

        # remove email login attempts
        db.query(LoginAttemptModel).filter(LoginAttemptModel.email == user.email).delete(synchronize_session="fetch")
        db.commit()

        return LoginResponse.from_orm(user)
    return ErrorResponse(Error.INVALID_CREDENTIALS)
