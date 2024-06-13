from sqlalchemy import create_engine
from  sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from db_config import URL

engine = create_engine(url= URL, echo=False)

class Base(DeclarativeBase):
    pass

session_factory = sessionmaker(engine)