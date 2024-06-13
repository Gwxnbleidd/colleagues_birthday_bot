import datetime
from sqlalchemy import and_, select, delete, update

from database import Base, engine, session_factory
from models import UsersTable, SubscriptionsTable

def create_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def add_user(id: int, name: str, birthday: datetime.date, password: str):
    with session_factory() as session:
        session.add(UsersTable(id=id, name=name, birthday=birthday, password=password))
        session.commit()

def subscribe(user_id: int, subscriptions_id: int):
    with session_factory() as session:
        session.add(SubscriptionsTable(user_id=user_id, subscriptions_id = subscriptions_id))
        session.commit()

def get_db():
    with session_factory() as session:
        query = select('*').select_from(UsersTable)
        res = session.execute(query)
        return res
    
# Взять пользователей, подписанных на subscriptions_id
def get_subscribers(subscriptions_id: int):
    with session_factory() as session:
        query = select(SubscriptionsTable.user_id).select_from(SubscriptionsTable).filter_by(subscriptions_id=subscriptions_id)
        res = session.scalars(query)
        return res.all()
    
def unsubscribe(user_id: int, subscriptions_id: int):
    with session_factory() as session:
        query = delete(SubscriptionsTable).where(and_(SubscriptionsTable.user_id==user_id, SubscriptionsTable.subscriptions_id==subscriptions_id))
        session.execute(query)
        session.commit()

# Получить список людей, на которых подписан id
def get_subscription_list(user_id:id) -> list:
    with session_factory() as session:
        query = (select(UsersTable.id, UsersTable.name)
                 .select_from(UsersTable)
                 .join(SubscriptionsTable, UsersTable.id == SubscriptionsTable.subscriptions_id)
                 .where(SubscriptionsTable.user_id==user_id))
        res = session.execute(query)
        return res

# Список людей, на которых id не подписан
def get_users_no_subs(user_id: int):
    with session_factory() as session:
        subquery = (select(UsersTable.id)
                 .select_from(UsersTable)
                 .join(SubscriptionsTable, UsersTable.id == SubscriptionsTable.subscriptions_id)
                 .where(SubscriptionsTable.user_id==user_id))

        subquery_list = [row[0] for row in session.execute(subquery)]

        query = (select(UsersTable.id, UsersTable.name)
                 .select_from(UsersTable)
                 .where(UsersTable.id.notin_(subquery_list))
                 .where(UsersTable.id != user_id) )
        
        res = session.execute(query)
        return res

def get_user_from_db(user_id: int):
    with session_factory() as session:
        res = session.get(UsersTable, user_id)
        return res
    
def update_name(user_id: int, new_name: str):
    with session_factory() as session:
        query = update(UsersTable).where(UsersTable.id==user_id).values(name=new_name)
        session.execute(query)
        session.commit()

def update_birthday(user_id: int, new_birthday: datetime.date):
    with session_factory() as session:
        query = update(UsersTable).where(UsersTable.id==user_id).values(birthday=new_birthday)
        session.execute(query)
        session.commit()