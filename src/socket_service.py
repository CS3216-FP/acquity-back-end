import jwt
import socketio
from src.config import APP_CONFIG
from src.services import (
    ChatService,
    ChatRoomService,
)

class ChatSocketService(socketio.AsyncNamespace):
    def __init__(self, namespace, config, ChatService=ChatService, ChatRoomService=ChatRoomService):
        super().__init__(namespace)
        self.ChatService = ChatService
        self.ChatRoomService = ChatRoomService
        self.config = config

    async def authenticate(self, encoded_token):
        decoded_token = jwt.decode(encoded_token, APP_CONFIG.get("SANIC_JWT_SECRET"), algorithms=['HS256'])
        user_id = decoded_token.get("id")
        return user_id

    async def join_chat_rooms(self, sid, user_id):
        rooms = self.ChatRoomService(self.config).get_chat_rooms(user_id=user_id)
        for room in rooms:
            self.enter_room(sid, room.get("chat_room_id"))
        self.enter_room(sid, user_id)
        return rooms

    async def on_connect(self, sid, environ):
        return {"data":"success"}

    async def on_disconnect(self, sid):
        return {"data":"success"}

    async def on_set_chat_list(self, sid, data):
        user_id = await self.authenticate(encoded_token=data.get("token"))
        rooms = await self.join_chat_rooms(sid=sid, user_id=user_id)
        await self.emit("get_chat_list", rooms, room=user_id)

    async def on_set_chat_room(self, sid, data):
        user_id = await self.authenticate(encoded_token=data.get("token"))
        conversation = self.ChatService(self.config).get_conversation(user_id=user_id, chat_room_id=data.get("chat_room_id"))
        await self.emit("get_chat_room", conversation, room=user_id)

    async def on_send_new_message(self, sid, data):
        user_id = await self.authenticate(encoded_token=data.get("token"))
        chat = self.ChatService(self.config).add_message(
            chat_room_id=data.get("chat_room_id"), 
            message=data.get("message"), 
            img=data.get("img"), 
            author_id=user_id)

        await self.emit("get_new_message", chat, room=chat.get("chat_room_id"))
