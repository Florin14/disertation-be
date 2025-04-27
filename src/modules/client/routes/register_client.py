from time import time

from fastapi import Depends
from jwt import encode
from sqlalchemy.orm import Session

from extensions import get_db
from modules.auth.models.confirm_email_token import ConfirmEmailToken
from modules.client.models import ClientModel
from project_helpers.config import platform
from project_helpers.error import Error
from project_helpers.functions import send_confirmation_email
from project_helpers.responses import ErrorResponse
from .router import router  # Assuming you have a router defined
from ..models.client_schemas import ClientResponse
from ..models.client_schemas import ClientRegister


@router.post("/register", response_model=ClientResponse)
async def create_client(data: ClientRegister, db: Session = Depends(get_db)):
    if data.password != data.confirmPassword:
        return ErrorResponse(Error.PASSWORDS_DO_NOT_MATCH)

    naturalPersonData = data.model_dump(exclude={"confirmPassword"})
    naturalPerson = ClientModel(**naturalPersonData, hasDefaultPassword=False)
    db.add(naturalPerson)
    db.flush()
    token = encode(
        {"email": naturalPerson.email, "expiresAt": time() + platform.TEMPORARY_PASSWORD_EXPIRATION_SECONDS},
        key=platform.SECRET_KEY,
        algorithm="HS512",
    )
    db.add(
        ConfirmEmailToken(
            userId=naturalPerson.id,
            email=naturalPerson.email,
            token=token,
        )
    )
    db.commit()
    send_confirmation_email(naturalPerson, token)

    db.refresh(naturalPerson)
    return naturalPerson
