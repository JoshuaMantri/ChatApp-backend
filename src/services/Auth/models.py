import pydantic

from datetime import datetime


class LoginPost(pydantic.BaseModel):
    email: str
    password: str

class UserModel(pydantic.BaseModel):
    user_id: int
    username: str
    email: str

class CreateAccountPost(pydantic.BaseModel):
    username: str
    email: str
    password: str

class AccessTokenModel(pydantic.BaseModel):
    expiry: datetime
    token: str