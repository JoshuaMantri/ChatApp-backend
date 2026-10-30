from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import os

from database.schema import create_tables

from services.Auth.store import AuthStore
from services.Auth.router import auth_router

from datetime import timedelta

dbPassword = os.environ["DB_ROOT_PASSWORD"]

engine = sa.create_engine(
    f"mysql+pymysql://root:{dbPassword}@db/chat_app?charset=utf8mb4"
)

create_tables(engine=engine)

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

Session = sa_orm.sessionmaker(engine)

with Session() as session:
    store = AuthStore(sa_session=session, session_validity_time=timedelta(seconds=300), jwt_validity_time=timedelta(seconds=100))
    # store.create_account(username="josh", email="joshmantri@icloud.com", password="password")
    # print(store.login(email="joshmantri@icloud.com", password="password"))
    # session.commit()


@app.get("/")
def read_root():
    return {"Hello": "World old world"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}