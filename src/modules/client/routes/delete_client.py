
from fastapi import Depends
from sqlalchemy.orm import Session

from extensions import get_db
from project_helpers.dependencies import GetInstanceFromPath, JwtRequired
from project_helpers.schemas import ConfirmationSchema
from .router import router
from ..models import ClientModel


@router.delete(
    "/{id}",
    response_model=ConfirmationSchema,
)
async def delete_client(
    client: ClientModel = Depends(GetInstanceFromPath(ClientModel)),
    db: Session = Depends(get_db),
):
    db.delete(client)
    db.commit()
    return ConfirmationSchema()
