from pydantic import BaseModel
from typing import List


class CreateGroup(BaseModel):
    name: str
    description: str


class GroupUsers(BaseModel):
    users: List[str]
