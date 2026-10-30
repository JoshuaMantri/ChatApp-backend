import sqlalchemy.orm as sa_orm
import sqlalchemy as sa

import secrets

from dataclasses import dataclass

from database.schema import User, UserSession

import bcrypt
import jwt
import pem

from datetime import datetime, timedelta, timezone
import time


class LoginError(Exception):
    """Incorrect email or password"""

class SessionError(Exception):
    """Incorrect or expired session token"""

@dataclass(kw_only=True, frozen=True)
class AuthStore():
    sa_session: sa_orm.Session
    session_validity_time: timedelta
    jwt_validity_time: timedelta

    def login(self, *, email : str, password : str) -> User:
        user = self.sa_session.scalars(
            sa.select(User)
            .where(User.email == email)
        ).one_or_none()
        if user is None:
            raise LoginError
        if (not self._check_password(user=user, password=password)):
            raise LoginError
        return user

    def create_account(self, *, username: str, email: str, password: str) -> User:
        password_hash = self._hash_password(password=password)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        self.sa_session.add(user)
        self.sa_session.flush()
        return user

    def create_access_token(self, *, session_token: str) -> str:
        session = self.sa_session.scalars(
            sa.select(UserSession)
            .where(UserSession.session_token == session_token)
        ).one()

        self._validate_session_token(session=session)

        with open("private_key.pem", "rb") as file:
            private_key = file.read()

        access_token = jwt.encode({
                "iat" : datetime.now(), 
                "exp" : datetime.now() + self.jwt_validity_time
            }, 
            private_key, algorithm="RS256")

        return access_token




    def _validate_session_token(self, *, session: UserSession):
        if session.session_expiry < datetime.now():
            raise SessionError
        
        

    def _hash_password(self, *, password: str) -> str:
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password=password.encode("UTF-8"), salt=salt)
        return password_hash.decode("UTF-8")

    def _check_password(self, *, user: User, password: str) -> bool:
        return bcrypt.checkpw(password=password.encode("UTF-8"), hashed_password=user.password_hash.encode("UTF-8"))

    def create_session_token(self, *, user_id: str) -> UserSession:
        token = secrets.token_urlsafe(32)
        timeStamp = datetime.now(timezone.utc)
        expiryTime = timeStamp + self.session_validity_time
        session = UserSession(
            session_token=token,
            user_id=user_id,
            session_expiry=expiryTime
        )
        self.sa_session.add(session)
        self.sa_session.commit()
        return session


