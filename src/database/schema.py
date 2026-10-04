import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

class Base(sa_orm.DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"

    id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True, autoincrement=True)
    username: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30))
    email: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30))
    password: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(50))


def create_tables(engine):
    Base.metadata.create_all(engine)
