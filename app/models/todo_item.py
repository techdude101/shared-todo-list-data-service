from pydantic import BaseModel


class TodoItem(BaseModel):
    id: int
    data: str
    completed: bool
    completed_timestamp: int
