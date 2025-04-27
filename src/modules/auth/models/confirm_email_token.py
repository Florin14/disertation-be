# Id: admin_model.py 202305 11/05/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202305
#   Date: 11/05/2023
#
# License description...
from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, String, BigInteger, ForeignKey, TEXT
from sqlalchemy.orm import relationship

from extensions import SqlBaseModel


class ConfirmEmailToken(SqlBaseModel):
    __tablename__ = "confirm_email_tokens"

    id = Column(BigInteger, primary_key=True)
    token = Column(TEXT, unique=True)
    email = Column(String(40), nullable=False)
    userId = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), name="user_id")
    user = relationship("UserModel", back_populates="confirmTokens")

    expiresAt = Column(
        DateTime, nullable=False, default=lambda: datetime.now() + timedelta(hours=48), name="expires_at"
    )
