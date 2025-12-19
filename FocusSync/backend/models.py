from pydantic import BaseModel
from typing import Optional

class SessionCreate(BaseModel):
    task_difficulty: int  # 1 (easy) to 5 (hard)

class SessionUpdate(BaseModel):
    distractions: int
    completed: bool