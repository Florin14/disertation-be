from fastapi import Depends
from sqlalchemy.orm import Session

from extensions import get_db
from extensions.auth_jwt import AuthJWT
from modules.auth.models.auth_schemas import LoginBody, LoginResponse
from modules.auth.models.login_attempt_model import LoginAttemptModel
from modules.user.models.user_model import UserModel
from project_helpers.error import Error
from project_helpers.functions import verify_password
from project_helpers.responses import ErrorResponse
from .router import router


@router.post("/login", response_model=LoginResponse)
def login(body: LoginBody, auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if user and verify_password(user.password, body.password):# and len(user.confirmTokens) == 0
        accessToken = auth.create_access_token(user.email, user_claims=user.getClaims())
        refreshToken = auth.create_refresh_token(user.email)
        # Set the JWT cookies in the response
        auth.set_access_cookies(accessToken)
        auth.set_refresh_cookies(refreshToken)

        # remove email login attempts
        db.query(LoginAttemptModel).filter(LoginAttemptModel.email == user.email).delete(synchronize_session="fetch")
        db.commit()
        return LoginResponse.from_orm(user)
    elif user and user.expiredConfirmations > 0:
        db.delete(user)
        db.commit()
    return ErrorResponse(Error.INVALID_CREDENTIALS)
