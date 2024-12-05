from pydantic import BaseModel
from typing import Union


class TodoItem(BaseModel):
    id: int
    data: str
    completed: bool
    completed_timestamp: Union[int, None]
