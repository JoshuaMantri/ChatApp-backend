import fastapi
import fastapi.security
import pydantic
import jwt

from dataclasses import dataclass

from services.Auth.models import UserClaims
from dependencies import require_jwt

message_router = fastapi.APIRouter(
    prefix="/message",
    tags=["messages"],
)

access_token_scheme = fastapi.security.HTTPBearer()

class Message(pydantic.BaseModel):
    id: int
    user: str
    message: str



class WebSocketHandler:
    def __init__(self, socket: fastapi.WebSocket):
        self.socket = socket
        self.authenticated = False

    def auth(self, token: str):
        self.token = token

        with open("public_key.pem", "rb") as file:
            public_key = file.read()

        token_claims = jwt.decode(token, key=public_key, algorithms="RS256")

        self.user_id = token_claims["user_id"]
        self.username = token_claims["username"]

        self.authenticated = True

        return True


class GroupChatHandler:
    def __init__(self):
        self.active_connections: dict[int, WebSocketHandler] = {}
        self.current_message_id: int = 0

    def connect(self, web_socket_handler: WebSocketHandler):
        if web_socket_handler.authenticated:
            self.active_connections[web_socket_handler.user_id] = web_socket_handler

    def disconnect(self, web_socket_handler: WebSocketHandler):
        self.active_connections.pop(web_socket_handler.user_id)

    async def broadcast(self, web_socket_handler: WebSocketHandler, message: str):
        if web_socket_handler.authenticated:
            message_data = Message(
                id=self.current_message_id,
                user=web_socket_handler.username,
                message=message,
            )
            self.current_message_id += 1

            message_data_json = message_data.model_dump()

            for user_id, handler in self.active_connections.items():
                del user_id
                await handler.socket.send_json(message_data_json)



    
gc = GroupChatHandler()

@message_router.websocket("")
async def message_socket(websocket: fastapi.WebSocket):
    await websocket.accept()
    web_socket_handler = WebSocketHandler(websocket)
    token = await websocket.receive_text()
    if web_socket_handler.auth(token):
        gc.connect(web_socket_handler)
        while True:
            try:
                data = await websocket.receive_text()
                await gc.broadcast(web_socket_handler, data)
            except fastapi.WebSocketDisconnect:
                gc.disconnect(web_socket_handler)
                print("disconnected", flush=True)
