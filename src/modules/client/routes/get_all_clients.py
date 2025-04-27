from sqlalchemy.orm import Session
from .router import router
from fastapi import Depends
from extensions import get_db
from ..models import ClientModel, ClientsListResponse, ClientsFilter


@router.get("", response_model=ClientsListResponse)
async def get_all_clients(query: ClientsFilter = Depends(), db: Session = Depends(get_db)):
    clientsQuery = db.query(ClientModel)
    clientsQuery = clientsQuery.order_by(
        getattr(getattr(ClientModel, query.sortBy), query.sortType)()
    )
    qty = clientsQuery.count()
    if None not in [query.offset, query.limit]:
        clientsQuery = clientsQuery.offset(query.offset).limit(query.limit)
    return ClientsListResponse(quantity=qty, items=clientsQuery.all())
