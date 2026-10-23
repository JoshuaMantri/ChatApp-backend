import fastapi
import typing

from services.Auth.models import LoginPost, CreateAccountPost, UserModel
from services.Auth.store import AuthStore
from dependencies import get_auth_store

auth_router = fastapi.APIRouter(
    prefix="/auth",
    tags="Authentication",
)

@auth_router.post("/login")
def login_user(response: fastapi.Response, loginDetails: LoginPost, store: typing.Annotated[AuthStore, fastapi.Depends(get_auth_store)]):
    user = store.login(email=loginDetails.email, password=loginDetails.password)
    session_token = store.create_session_token(user_id=user.user_id)
    response.set_cookie(key="session_token", value=session_token.session_token, expires=session_token.session_expiry, httponly=True, samesite="strict", secure=True)
    return UserModel (
        user_id=user.user_id,
        username=user.username,
        email=user.email,
    )

@auth_router.get("/access_token")
def get_access_token(request: fastapi.Request, store: typing.Annotated[AuthStore, fastapi.Depends(get_auth_store)]):
    session_token = request.cookies.get("session_token")
    access_token = store.create_access_token(session_token=session_token)
    return {"access_token": access_token}

@auth_router.post("/create_account")
def create_user_account(accountDetails: CreateAccountPost, store: typing.Annotated[AuthStore, fastapi.Depends(get_auth_store)]):
    user = store.create_account(username=accountDetails.username, email=accountDetails.email, password=accountDetails.password)
    return UserModel(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
    )