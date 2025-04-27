from fastapi import Depends
from sqlalchemy.orm import Session

from extensions import get_db
from project_helpers.dependencies import GetInstanceFromPath
from .router import router
from ..models import ClientModel, ClientUpdate, ClientResponse


@router.put(
    "/{id}",
    response_model=ClientResponse,
)
async def update_client(
        data: ClientUpdate,
        client: ClientModel = Depends(GetInstanceFromPath(ClientModel)),
        db: Session = Depends(get_db),
):
    client.update(data, exclude_unset=True, exclude_none=False)

    db.commit()

    return client
