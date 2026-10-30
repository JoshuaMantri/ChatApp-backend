import fastapi
import fastapi.security
import typing
import datetime
from services.Auth.models import LoginPost, CreateAccountPost, UserModel, AccessTokenModel
from services.Auth.store import AuthStore
from dependencies import get_auth_store

auth_router = fastapi.APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

session_token_scheme = fastapi.security.APIKeyCookie(
    name="session_token"
)

@auth_router.post("/login")
def login_user(response: fastapi.Response, loginDetails: LoginPost, store: typing.Annotated[AuthStore, fastapi.Depends(get_auth_store)]) -> UserModel:
    user = store.login(email=loginDetails.email, password=loginDetails.password)
    session_token = store.create_session_token(user_id=user.user_id)
    expires = session_token.session_expiry.replace(tzinfo=datetime.timezone.utc)
    response.set_cookie(key="session_token", value=session_token.session_token, expires=expires, httponly=False, samesite="strict", secure=False)
    store.sa_session.commit()
    return UserModel (
        user_id=user.user_id,
        username=user.username,
        email=user.email,
    )

@auth_router.get("/access_token")
def get_access_token(request: fastapi.Request, store: typing.Annotated[AuthStore, fastapi.Depends(get_auth_store)], session_token: typing.Annotated[str, fastapi.Depends(session_token_scheme)]) -> AccessTokenModel:
    access_token = store.create_access_token(session_token=session_token)
    store.sa_session.commit()
    return AccessTokenModel(
        token=access_token,
        expiry= datetime.datetime.now() + store.jwt_validity_time
    )

@auth_router.post("/create_account")
def create_user_account(accountDetails: CreateAccountPost, store: typing.Annotated[AuthStore, fastapi.Depends(get_auth_store)]) -> UserModel:
    user = store.create_account(username=accountDetails.username, email=accountDetails.email, password=accountDetails.password)
    store.sa_session.commit()
    return UserModel(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
    )