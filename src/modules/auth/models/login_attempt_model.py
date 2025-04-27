# Id: login_attempt_model.py 202307 21/07/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202307
#   Date: 21/07/2023
#
# License description...
from datetime import datetime, timedelta
from sqlalchemy import Column, String, BigInteger, DateTime
from extensions import SqlBaseModel


class LoginAttemptModel(SqlBaseModel):
    __tablename__ = "login-attempt"
    email = Column(String(50), primary_key=True, nullable=False, unique=True)
    attempt = Column(BigInteger, nullable=False, default=3, server_default="3")
    exp = Column(DateTime, nullable=True, default=datetime.now() + timedelta(hours=24))
