import pytest
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from database.schema import User, UserSession
from services.Auth.store import AuthStore, LoginError

from database.schema import create_tables

from services.Auth.store import SessionError

import datetime

import jwt

import pem

TEST_CURRENT_TIME = datetime.datetime(year=2000, month=1, day=1, hour=0, minute=1, second=0)
TEST_SESSION_EXPIRY_TIME = datetime.timedelta(minutes=1)
TEST_JWT_EXPIRTY_TIME = datetime.timedelta(minutes=2)
TEST_EXPIRED_TIME = datetime.datetime(year=2030, month=1, day=1, hour=0, minute=1, second=0)

@pytest.fixture
def get_session() -> sa_orm.Session:
    engine = sa.create_engine("sqlite:///:memory:")
    create_tables(engine=engine)
    session = sa_orm.create_session(engine)
    return session

@pytest.fixture
def auth_store(get_session: sa_orm.Session) -> AuthStore:
    return AuthStore(
        sa_session=get_session,
        session_validity_time=TEST_SESSION_EXPIRY_TIME,
        jwt_validity_time=TEST_JWT_EXPIRTY_TIME,
    )


@pytest.fixture
def user_catalogue(get_session: sa_orm.Session, auth_store: AuthStore) -> None:
    user = User(
        user_id=1,
        username="josh",
        email="joshmantri@icloud.com",
        password_hash=auth_store._hash_password(password="password"),
    )
    get_session.add(user)
    get_session.commit()

    return user

@pytest.fixture
def session_catalogue(get_session: sa_orm.Session, auth_store: AuthStore) -> None:
    session = UserSession(
        user_id=1,
        session_token="token",
        session_expiry=TEST_CURRENT_TIME + TEST_SESSION_EXPIRY_TIME,
    )
    get_session.add(session)
    get_session.commit()

@pytest.fixture
def public_key() -> str:
    with open("public_key.pem") as file:
        return file.read()



def test_user_login_with_password(auth_store: AuthStore, user_catalogue: User):
    del user_catalogue
    assert auth_store.login(email="joshmantri@icloud.com", password="password")

def test_incorrect_user_email_login_fails(auth_store: AuthStore, user_catalogue: User):
    del user_catalogue
    with pytest.raises(LoginError):
        auth_store.login(email="fakeperson@gmail.com", password="password")

def test_incorrect_user_password_login_fails(auth_store: AuthStore, user_catalogue: User):
    del user_catalogue
    with pytest.raises(LoginError):
        auth_store.login(email="joshmantri@icloud.com", password="fakePassword")

@pytest.mark.time_machine(TEST_CURRENT_TIME, tick=False)
def test_create_session_token_generates_a_token(auth_store: AuthStore, user_catalogue: User, get_session: sa_orm.Session):
    auth_store.create_session_token(user_id=user_catalogue.user_id)
    session = get_session.scalars(
        sa.select(UserSession)
        .where(UserSession.user_id == user_catalogue.user_id)
    ).one()

    assert session.session_token is not None
    assert session.session_expiry == TEST_CURRENT_TIME + TEST_SESSION_EXPIRY_TIME

@pytest.mark.time_machine(TEST_EXPIRED_TIME, tick=False)
def test_expired_session_token_rejected(auth_store: AuthStore, user_catalogue: User, session_catalogue: sa_orm.Session):
    del user_catalogue
    del session_catalogue

    with pytest.raises(SessionError):
        auth_store.create_access_token(session_token="token")


@pytest.mark.time_machine(TEST_CURRENT_TIME, tick=False)
def test_get_access_token_claims(auth_store: AuthStore, public_key: str, user_catalogue: None, session_catalogue: None):
    del user_catalogue
    del session_catalogue

    claims = jwt.decode(auth_store.create_access_token(session_token="token"), key=public_key, algorithms=["RS256"])

    assert claims["iat"] == TEST_CURRENT_TIME.timestamp()
    assert claims["exp"] == (TEST_CURRENT_TIME + TEST_JWT_EXPIRTY_TIME).timestamp()


def test_create_account(auth_store: AuthStore, get_session: sa_orm.Session):
    auth_store.create_account(username="josh", email="joshmantri@icloud.com", password="test")
    get_session.commit()
    assert auth_store.login(email="joshmantri@icloud.com", password="test")

