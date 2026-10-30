import os
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import fastapi
import typing
import datetime

from services.Auth.store import AuthStore


db_password = os.environ["DB_ROOT_PASSWORD"]
engine = sa.create_engine(
    f"mysql+pymysql://root:{db_password}@db/chat_app?charset=utf8mb4"
)
session_maker = sa_orm.sessionmaker(engine)

def get_db_connection():
    with session_maker() as session:
        yield session

def get_auth_store(sa_session: typing.Annotated[sa_orm.Session, fastapi.Depends(get_db_connection)]):
    session_validity_time = datetime.timedelta(seconds=int(os.environ["SESSION_VALIDITY_TIME"]))
    jwt_validity_time = datetime.timedelta(seconds=int(os.environ["JWT_VALIDITY_TIME"]))

    return AuthStore(sa_session=sa_session, session_validity_time=session_validity_time, jwt_validity_time=jwt_validity_time)
