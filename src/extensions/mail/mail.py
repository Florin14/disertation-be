
import os
import smtplib
from typing import List, IO
from jinja2 import Environment, PackageLoader, select_autoescape
from pydantic import Field, EmailStr
from fastapi_mail import ConnectionConfig
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from constants import PlatformEnvs


class MailConfig(ConnectionConfig):
    MAIL_USERNAME: str = Field("zimbru.florin.4@gmail.com", env="MAIL_USERNAME")
    MAIL_PASSWORD: str = Field("Castigator1.", env="MAIL_PASSWORD")
    MAIL_FROM: EmailStr = Field("zimbru.florin.4@gmail.com", env="MAIL_FROM")
    MAIL_SERVER: str = Field("smtp.gmail.com", env="MAIL_SERVER")
    TEMPLATE_FOLDER: str = "templates"
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_DEV_RECIPIENT: str = Field("c.icadacws@gmail.com", env="MAIL_DEV_RECIPIENT")
    MAIL_DEV_CC: str = Field("c.i.cadacws@gmail.com", env="MAIL_DEV_RECIPIENT")
    MAIL_DEV_BCC: str = Field("c.i.c.adacws@gmail.com", env="MAIL_DEV_RECIPIENT")


env = Environment(
    loader=PackageLoader("templates", os.environ.get("TEMPLATES_PATH", "/")),
    autoescape=select_autoescape(["html", "xml"]),
)


def get_template(template, *args, **kwargs):
    template = env.get_template(template)
    return template.render(*args, **kwargs)


def send_html_email(
    template: str,
    subject: str,
    recipients: List,
    sender: tuple = None,  # (email, password)
    cc: List = None,
    bcc: List = None,
    attachments: List[tuple[str, IO]] = None,
    config=MailConfig(),
    *args,
    **kwargs,
):
    html = get_template(template=template, *args, **kwargs)

    sEmail, sPassword = sender or (config.MAIL_FROM, config.MAIL_PASSWORD)

    openServer = smtplib.SMTP

    if (
        PlatformEnvs.LOCAL.match()
        or PlatformEnvs.DEVELOPMENT.match()
        or PlatformEnvs.STAGING.match()
        or PlatformEnvs.PREPRODUCTION.match()
        or PlatformEnvs.TESTING.match()
    ):
        openServer = smtplib.SMTP_SSL
        subject = subject + f" (TO: {recipients}, CC: {cc}, BCC: {bcc})"
        recipients = [config.MAIL_DEV_RECIPIENT]
        if cc:
            cc = [config.MAIL_DEV_CC]
        if bcc:
            bcc = [config.MAIL_DEV_BCC]

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sEmail
    message["To"] = ", ".join(recipients)
    message["Cc"] = ",".join(cc or [])
    message["Bcc"] = ",".join(bcc or [])

    message.attach(MIMEText(html, "html"))

    if attachments:
        for fileName, file in attachments:
            if isinstance(file, IO):
                filePart = MIMEApplication(file.read())
                filePart.add_header("Content-Disposition", "attachment", filename=fileName)
                message.attach(filePart)
            else:
                raise TypeError("File type must be IO binary type!")

    with openServer(config.MAIL_SERVER, config.MAIL_PORT) as server:
        if config.MAIL_STARTTLS:
            server.starttls()
        server.login(sEmail, sPassword)
        server.sendmail(sEmail, [*recipients, *(cc or []), *(bcc or [])], message.as_string())
