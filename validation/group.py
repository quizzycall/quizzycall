from pydantic import BaseModel


class CreateGroup(BaseModel):
    name: str
    description: str
