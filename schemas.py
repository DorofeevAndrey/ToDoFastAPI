from pydantic import BaseModel
from typing import Optional


class Login(BaseModel):
    name: str
    password: str


class Task(BaseModel):
    task: str
    done: bool = False


class ItemId(BaseModel):
    id: int


class TaskToChange(ItemId):
    task: Optional[str] = None
    done: Optional[bool] = None
