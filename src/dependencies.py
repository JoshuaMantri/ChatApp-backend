import os
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import fastapi
import typing
import datetime
import fastapi
import fastapi.security
import jwt

from services.Auth.store import AuthStore

from services.Auth.models import UserClaims

access_token_scheme = fastapi.security.HTTPBearer()


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


def require_jwt(token: typing.Annotated[fastapi.security.HTTPAuthorizationCredentials, fastapi.Depends(access_token_scheme)]):
    with open("public_key.pem", "rb") as file:
        public_key = file.read()

    token = jwt.decode(token.credentials, key=public_key, algorithms="RS256")

    return UserClaims(
        user_id=token["user_id"]
    )
