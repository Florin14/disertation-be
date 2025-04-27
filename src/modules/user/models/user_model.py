from datetime import datetime

from sqlalchemy import Column, DateTime, String, BigInteger, Enum, Boolean, Unicode, exists, and_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from constants import PlatformRoles
from extensions import SqlBaseModel
from project_helpers.functions import hash_password


class UserModel(SqlBaseModel):
    __tablename__ = "users"

    unhashed_password = ""

    id = Column(BigInteger, primary_key=True)
    email = Column(String(40), nullable=False, unique=True)
    name = Column(Unicode(50))
    _password = Column(String(300), nullable=False)
    role = Column(Enum(PlatformRoles), nullable=False)
    hasDefaultPassword = Column(Boolean, nullable=False, default=True, name="has_default_password")
    isAvailable = Column(Boolean, default=True, server_default="True", name="is_available")
    createDate = Column(DateTime, default=datetime.now, name="create_date")
    phoneNumber = Column(String(20), unique=True, name="phone_number")

    confirmTokens = relationship("ConfirmEmailToken", cascade="all,delete", back_populates="user")

    # on new search vector add :
    # migrations/script.py.mako -> in upgrade_trigger() function you should add:
    # sync_trigger(conn, 'users', 'search_vector', ['name'])

    # on search vector delete:
    # migrations/script.py.mako -> in upgrade_trigger() function you should delete:
    # sync_trigger(conn, 'users', 'search_vector', ['name'])

    # on search vector update:
    # ex. search_vector = Column(TSVectorType('name', 'email', auto_index=True))
    # migrations/script.py.mako -> in upgrade_trigger() function you should update:
    # sync_trigger(conn, 'users', 'search_vector', ['name', 'email'])

    search_vector = Column(TSVectorType("name", auto_index=True))

    __mapper_args__ = {"polymorphic_identity": "users", "polymorphic_on": "role"}

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self.unhashed_password = value
        self._password = hash_password(value)

    def getClaims(self):
        return {
            "userId": self.id,
            "role": self.role.name,
            "userName": self.name,
        }

    @hybrid_property
    def expiredConfirmations(self):
        return len([token for token in self.confirmTokens or [] if token.expiresAt < datetime.now()])

    @hybrid_property
    def hasExpiredConfirmation(self):
        return any(token.expiresAt < datetime.now() for token in self.confirmTokens or [])

    @hasExpiredConfirmation.expression
    def hasExpiredConfirmation(cls):
        from modules.auth.models.confirm_email_token import ConfirmEmailToken

        return exists().where(and_(ConfirmEmailToken.userId == cls.id, ConfirmEmailToken.expiresAt < datetime.now()))

    @hybrid_property
    def isAccountConfirmed(self):
        return self.confirmTokens is None

    @isAccountConfirmed.expression
    def isAccountConfirmed(cls):
        from modules.auth.models.confirm_email_token import ConfirmEmailToken

        return ~exists().where(ConfirmEmailToken.userId == cls.id)
