import socketio

from src.services import ChatRoomService, ChatService, LinkedInLogin, UserService


class ChatSocketService(socketio.AsyncNamespace):
    def __init__(self, namespace, config, sio):
        super().__init__(namespace)
        self.chat_service = ChatService(config)
        self.chat_room_service = ChatRoomService(config)
        self.linkedin_login = LinkedInLogin(config, sio)
        self.user_service = UserService(config)
        self.config = config

    async def authenticate(self, token):
        linkedin_user = self.linkedin_login.get_user_profile(token=token)
        user = self.user_service.get_user_by_linkedin_id(
            user_id=linkedin_user.get("user_id")
        )
        return user.get("id")

    async def join_chat_rooms(self, sid, user_id):
        rooms = self.chat_room_service.get_chat_rooms(user_id=user_id)
        for room in rooms:
            self.enter_room(sid, room.get("chat_room_id"))
        self.enter_room(sid, user_id)
        return rooms

    async def on_connect(self, sid, environ):
        return {"data": "success"}

    async def on_disconnect(self, sid):
        return {"data": "success"}

    async def on_set_chat_list(self, sid, data):
        user_id = await self.authenticate(token=data.get("token"))
        rooms = await self.join_chat_rooms(sid=sid, user_id=user_id)
        await self.emit("get_chat_list", rooms, room=user_id)

    async def on_set_chat_room(self, sid, data):
        user_id = await self.authenticate(token=data.get("token"))
        conversation = self.chat_service.get_conversation(
            user_id=user_id, chat_room_id=data.get("chat_room_id")
        )
        await self.emit("get_chat_room", conversation, room=user_id)

    async def on_set_new_message(self, sid, data):
        user_id = await self.authenticate(token=data.get("token"))
        chat = self.chat_service.add_message(
            chat_room_id=data.get("chat_room_id"),
            message=data.get("message"),
            author_id=user_id,
        )

        await self.emit("get_new_message", chat, room=chat.get("chatRoomId"))

    async def on_set_other_party_details(self, sid, data):
        user_id = await self.authenticate(token=data.get("token"))
        room_id = data.get("chat_room_id")

        other_party_details = self.chat_room_service.get_other_party_details(
            chat_room_id=room_id, user_id=user_id
        )

        await self.emit("get_other_party_details", other_party_details, room=room_id)
