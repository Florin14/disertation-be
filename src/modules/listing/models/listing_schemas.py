from typing import List

from project_helpers.schemas import BaseSchema, FilterSchema


class ListingAdd(BaseSchema):
    pass


class ListingUpdate(BaseSchema):
    pass


class ListingFilter(FilterSchema):
    sortBy: str = "companyName"


class ListingResponse(BaseSchema):
    pass


class ListingItem(BaseSchema):
    pass


class ListingListResponse(BaseSchema):
    quantity: int
    items: List[ListingItem]
