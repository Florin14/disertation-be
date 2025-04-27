
from time import time

from sqlalchemy import Column, String, BigInteger
from extensions import SqlBaseModel, SessionLocal
from extensions.auth_jwt import AuthJWT


class BlacklistModel(SqlBaseModel):
    __tablename__ = "blacklist"

    id = Column(BigInteger, primary_key=True, unique=True)
    exp = Column(BigInteger, nullable=True)
    token = Column(String(300), nullable=False, unique=True)


@AuthJWT.token_in_denylist_loader
def check_if_token_in_blacklist(decrypted_token):
    with SessionLocal() as db:
        currentTime = time()
        blQuery = db.query(BlacklistModel).filter(BlacklistModel.exp <= int(currentTime))
        blQuery.delete(synchronize_session="fetch")
        return db.query(BlacklistModel).filter(BlacklistModel.token == decrypted_token["jti"]).count()
