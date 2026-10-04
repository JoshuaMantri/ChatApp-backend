from fastapi import FastAPI

from sqlalchemy import create_engine
import os

from database.schema import create_tables

dbPassword = os.environ["DB_ROOT_PASSWORD"]

engine = create_engine(
    f"mysql+pymysql://root:{dbPassword}@db/chat_app?charset=utf8mb4"
)

create_tables(engine=engine)

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World old world"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}