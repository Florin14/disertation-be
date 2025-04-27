

from fastapi import Depends
from sqlalchemy.orm import Session

from extensions import get_db
from .router import router
from ..models import ClientModel, ClientAdd, ClientItem


@router.post(
    "",
    response_model=ClientItem,
)
async def add_client(data: ClientAdd, db: Session = Depends(get_db)):
    password = "Castigator1."

    client = ClientModel(**data.dict(), password=password)
    db.add(client)
    db.commit()
    return client
