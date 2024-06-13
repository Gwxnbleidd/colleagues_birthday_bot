from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
import datetime

from database import Base

class UsersTable(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    birthday: Mapped[datetime.date]
    password: Mapped[str]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, birthday={self.birthday!r})"

class SubscriptionsTable(Base):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    subscriptions_id: Mapped[int] = mapped_column(ForeignKey('users.id',ondelete='CASCADE'))

    def __repr__(self) -> str:
        return f"Subscription(user_id={self.user_id!r}, subscriptions_id={self.subscriptions_id!r})"
    