from fastapi import Depends
from pydantic import BaseModel
# from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from extensions.auth_jwt import AuthJWT
from modules.auth.models.auth_schemas import LoginResponse
from modules.user.models.user_model import UserModel
from project_helpers.responses import ErrorResponse
from .router import router
from extensions import get_db
from project_helpers.error import Error
from .verify_google_token import verify_google_token


class SocialLoginBody(BaseModel):
    credential: str
    provider: str


@router.post("/social-login", response_model=LoginResponse)
def social_login(
        body: SocialLoginBody,
        auth: AuthJWT = Depends(),
        db: Session = Depends(get_db),
):
    # 1. Verificăm că provider-ul e „google”
    if body.provider.lower() != "google":
        return ErrorResponse(Error.INVALID_PROVIDER)

    # 2. Validăm token-ul Google și extragem informaţiile
    idinfo = verify_google_token(body.credential)
    if not idinfo:
        return ErrorResponse(Error.INVALID_CREDENTIALS)

    email = idinfo["email"]
    # 3. Căutăm user-ul existent sau îl creăm
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        user = UserModel(
            email=email,
            name=idinfo.get("name"),
            google_id=idinfo["sub"],
            has_default_password=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 4. Generăm JWT-urile și le setăm ca şi cookie-uri
    access_token = auth.create_access_token(email, user_claims=user.getClaims())
    refresh_token = auth.create_refresh_token(email)
    auth.set_access_cookies(access_token)
    auth.set_refresh_cookies(refresh_token)

    return LoginResponse.from_orm(user)
