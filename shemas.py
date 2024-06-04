from pydantic import BaseModel
import datetime

class User(BaseModel):
    id: int
    name: str
    birthday: datetime.date