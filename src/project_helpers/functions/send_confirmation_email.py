# Created by: cicada
# Date: Wed 04/09/2025
# Time: 13:00:33.38
import logging

from constants import CONFIRM_ACCOUNT_SUBJECT
from extensions import send_html_email
from project_helpers.config import platform


def send_confirmation_email(target, token: str):
    from modules.legal_entities.models.legal_entities_model import LegalEntitiesModel
    from modules.natural_persons.models.natural_persons_model import NaturalPersonsModel

    target: LegalEntitiesModel | NaturalPersonsModel
    try:
        url = f"{platform.FRONTEND_URL}/login?code={token}&email={target.email}"
        send_html_email(
            template="confirm_account_template.html",
            subject=CONFIRM_ACCOUNT_SUBJECT,
            recipients=[target.email],
            name=target.name,
            email=target.email,
            password=target.unhashed_password,
            path=url,
            translate=lambda a: a,
        )
    except Exception as e:
        logging.warning(str(e))
