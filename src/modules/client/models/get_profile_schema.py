from project_helpers.schemas import BaseSchema


class ClientProfileResponse(BaseSchema):
    id: int
    name: str
    email: str
    phoneNumber: str
