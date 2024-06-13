from pydantic import BaseModel
import datetime

class User(BaseModel):
    id: int
    name: str
    birthday: datetime.date
    password: str | None
    # session_token: str | None

class Subscription(BaseModel):
    user_id: int
    subscriptions_id: int