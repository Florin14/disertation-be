
from sqlalchemy.orm import Session

from extensions import get_db
from .router import router
from fastapi import Depends
from project_helpers.dependencies import GetInstanceFromPath
from ..models import ClientModel, ClientResponse


@router.get("/{id}", response_model=ClientResponse)
async def get_client(
    client: ClientModel = Depends(GetInstanceFromPath(ClientModel)),
):
    return client
