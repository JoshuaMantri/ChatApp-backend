import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from datetime import datetime

class Base(sa_orm.DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"

    user_id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True, autoincrement=True)
    username: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30))
    email: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30))
    password_hash: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255))
    session: sa_orm.Mapped[list["UserSession"]] = sa_orm.relationship("UserSession", back_populates="user")

class UserSession(Base):
    __tablename__ = "user_session"

    session_token: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(50), primary_key=True)
    user_id = sa_orm.mapped_column(sa.ForeignKey("user_account.user_id"))
    session_expiry : sa_orm.Mapped[datetime] = sa_orm.mapped_column(sa.TIMESTAMP)

    user: sa_orm.Mapped[User] = sa_orm.relationship("User", back_populates="session")


def create_tables(engine):
    Base.metadata.create_all(engine)
