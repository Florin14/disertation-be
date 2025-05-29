import logging

from constants import CONFIRM_ACCOUNT_SUBJECT
from extensions import send_html_email


def send_confirmation_email(target, token: str):
    from modules.client.models.client_model import ClientModel

    target: ClientModel
    try:
        url = f"http://localhost:3000/login?code={token}&email={target.email}"
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
