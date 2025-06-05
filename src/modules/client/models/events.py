import logging
from datetime import datetime

from sqlalchemy import event

from constants import ACCOUNT_CREATED_SUBJECT
from constants import PlatformRoles
from extensions import SessionLocal
from extensions import send_html_email
from modules.auth.models import ConfirmEmailToken
from modules.client.models.client_model import ClientModel
from modules.user.models.user_model import UserModel


@event.listens_for(ClientModel, "before_insert")
def send_account_verify_token_notification_email(mapper, connection, target: ClientModel):
    with SessionLocal() as db:
        user = db.query(UserModel).filter(UserModel.email == target.email).first()
        confirmTokens = db.query(ConfirmEmailToken).filter(ConfirmEmailToken.email == target.email)

        availableTokens = confirmTokens.filter(ConfirmEmailToken.expiresAt >= datetime.now())

        if user and user.role == PlatformRoles.CLIENT and availableTokens.count() > 0:
            db.delete(user)
            db.commit()


@event.listens_for(ClientModel, "after_insert")
def send_account_created_notification_email(mapper, connection, target: ClientModel):
    if not target.hasDefaultPassword:
        return
    try:
        send_html_email(
            template="account_created.html",
            subject=ACCOUNT_CREATED_SUBJECT,
            recipients=[target.email],
            name=target.name,
            email="zimbru.florin.4@gmail.com",
            url=f"http://localhost:3000",
            password=target.unhashed_password,
            translate=lambda a: a,
            hasDefaultPassword=True,
        )
    except Exception as e:
        logging.warning(str(e))
