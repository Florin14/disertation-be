
from sqlalchemy import Column, BigInteger, ForeignKey

from constants import PlatformRoles
from modules.user.models.user_model import UserModel


class ClientModel(UserModel):
    __tablename__ = "clients"
    id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    __mapper_args__ = {
        "inherit_condition": (id == UserModel.id),
        "polymorphic_identity": PlatformRoles.CLIENT,
    }