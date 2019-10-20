import datetime
from datetime import datetime
from operator import itemgetter
import requests
from passlib.hash import argon2
from sqlalchemy import desc, asc
from sqlalchemy import or_, and_
from src.config import APP_CONFIG
from src.database import Security, SellOrder, User, ChatRoom, Chat, session_scope
from src.exceptions import InvalidRequestException, UnauthorizedException
from src.schemata import (
    CREATE_SELL_ORDER_SCHEMA,
    CREATE_USER_SCHEMA,
    DELETE_SELL_ORDER_SCHEMA,
    EDIT_SELL_ORDER_SCHEMA,
    EMAIL_RULE,
    INVITE_SCHEMA,
    LINKEDIN_BUYER_PRIVILEGES_SCHEMA,
    LINKEDIN_CODE_SCHEMA,
    LINKEDIN_MATCH_EMAILS_SCHEMA,
    LINKEDIN_TOKEN_SCHEMA,
    USER_AUTH_SCHEMA,
    UUID_RULE,
    validate_input,
)
import socketio
import jwt


class UserService:
    def __init__(self, User=User, hasher=argon2):
        self.User = User
        self.hasher = hasher

    @validate_input(CREATE_USER_SCHEMA)
    def create(self, email, password, full_name):
        with session_scope() as session:
            hashed_password = self.hasher.hash(password)
            user = self.User(
                email=email,
                full_name=full_name,
                hashed_password=hashed_password,
                can_buy=False,
                can_sell=False,
            )
            session.add(user)
            session.commit()

            result = user.asdict()
        result.pop("hashed_password")
        return result

    @validate_input({"user_id": UUID_RULE})
    def activate_buy_privileges(self, user_id):
        with session_scope() as session:
            user = session.query(self.User).filter_by(id=user_id).one()
            user.can_buy = True
            session.commit()
            result = user.asdict()
        result.pop("hashed_password")
        return result

    @validate_input(INVITE_SCHEMA)
    def invite_to_be_seller(self, inviter_id, invited_id):
        with session_scope() as session:
            inviter = session.query(self.User).filter_by(id=inviter_id).one()
            if not inviter.can_sell:
                raise UnauthorizedException("Inviter is not a previous seller.")

            invited = session.query(self.User).filter_by(id=invited_id).one()
            invited.can_sell = True

            session.commit()

            result = invited.asdict()
        result.pop("hashed_password")
        return result

    @validate_input(USER_AUTH_SCHEMA)
    def authenticate(self, email, password):
        with session_scope() as session:
            user = session.query(self.User).filter_by(email=email).one()
            if self.hasher.verify(password, user.hashed_password):
                return user.asdict()
            else:
                return None

    @validate_input({"id": UUID_RULE})
    def get_user(self, id):
        with session_scope() as session:
            user = session.query(self.User).filter_by(id=id).one().asdict()
        user.pop("hashed_password")
        return user

    @validate_input({"email": EMAIL_RULE})
    def get_user_by_email(self, email):
        with session_scope() as session:
            user = session.query(self.User).filter_by(email=email).one().asdict()
        user.pop("hashed_password")
        return user


class SellOrderService:
    def __init__(self, SellOrder=SellOrder, User=User):
        self.SellOrder = SellOrder
        self.User = User

    @validate_input(CREATE_SELL_ORDER_SCHEMA)
    def create_order(self, user_id, number_of_shares, price, security_id):
        with session_scope() as session:
            user = session.query(self.User).filter_by(id=user_id).one()
            if not user.can_sell:
                raise UnauthorizedException("This user cannot sell securities.")

            sell_order = self.SellOrder(
                user_id=user_id,
                number_of_shares=number_of_shares,
                price=price,
                security_id=security_id,
            )

            session.add(sell_order)
            session.commit()
            return sell_order.asdict()

    @validate_input({"user_id": UUID_RULE})
    def get_orders_by_user(self, user_id):
        with session_scope() as session:
            sell_orders = session.query(self.SellOrder).filter_by(user_id=user_id).all()
            return [sell_order.asdict() for sell_order in sell_orders]

    @validate_input(EDIT_SELL_ORDER_SCHEMA)
    def edit_order(self, id, subject_id, new_number_of_shares=None, new_price=None):
        with session_scope() as session:
            sell_order = session.query(self.SellOrder).filter_by(id=id).one()
            if sell_order.user_id != subject_id:
                raise UnauthorizedException("You need to own this order.")

            if new_number_of_shares is not None:
                sell_order.number_of_shares = new_number_of_shares
            if new_price is not None:
                sell_order.price = new_price

            session.commit()
            return sell_order.asdict()

    @validate_input(DELETE_SELL_ORDER_SCHEMA)
    def delete_order(self, id, subject_id):
        with session_scope() as session:
            sell_order = session.query(self.SellOrder).filter_by(id=id).one()
            if sell_order.user_id != subject_id:
                raise UnauthorizedException("You need to own this order.")

            session.delete(sell_order)
        return {}


class SecurityService:
    def __init__(self, Security=Security):
        self.Security = Security

    def get_all(self):
        with session_scope() as session:
            return [sec.asdict() for sec in session.query(self.Security).all()]


class LinkedinService:
    def __init__(self, User=User, UserService=UserService):
        self.User = User
        self.UserService = UserService

    @validate_input(LINKEDIN_BUYER_PRIVILEGES_SCHEMA)
    def activate_buyer_privileges(self, code, redirect_uri, user_email):
        linkedin_email = self.get_user_data(code=code, redirect_uri=redirect_uri)
        is_email = self.is_match(linkedin_email=linkedin_email, user_email=user_email)
        if is_email:
            user = self.UserService().get_user_by_email(email=user_email)
            return self.UserService().activate_buy_privileges(user_id=user.get("id"))
        else:
            raise InvalidRequestException("Linkedin email does not match")

    @validate_input(LINKEDIN_CODE_SCHEMA)
    def get_user_data(self, code, redirect_uri):
        token = self.get_token(code=code, redirect_uri=redirect_uri)
        return self.get_user_email(token=token)

    @validate_input(LINKEDIN_CODE_SCHEMA)
    def get_token(self, code, redirect_uri):
        token = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            headers={"Content-Type": "x-www-form-urlencoded"},
            params={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": APP_CONFIG.get("CLIENT_ID"),
                "client_secret": APP_CONFIG.get("CLIENT_SECRET"),
            },
        ).json()
        return token.get("access_token")

    @validate_input(LINKEDIN_TOKEN_SCHEMA)
    def get_user_profile(self, token):
        user_profile = requests.get(
            "https://api.linkedin.com/v2/me",
            headers={"Authorization": f"Bearer {token}"},
        ).json()
        first_name = user_profile.get("localizedFirstName")
        last_name = user_profile.get("localizedLastName")
        return {"full_name": f"{first_name} {last_name}"}

    @validate_input(LINKEDIN_TOKEN_SCHEMA)
    def get_user_email(self, token):
        email = requests.get(
            "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
            headers={"Authorization": f"Bearer {token}"},
        ).json()
        return email.get("elements")[0].get("handle~").get("emailAddress")

    @validate_input(LINKEDIN_MATCH_EMAILS_SCHEMA)
    def is_match(self, user_email, linkedin_email):
        return True if user_email == linkedin_email else False


class ChatService:
    def __init__(self, UserService=UserService, Chat=Chat, ChatRoom=ChatRoom):
        self.Chat = Chat
        self.UserService = UserService
        self.ChatRoom = ChatRoom

    def get_last_message(self, chat_room_id):
        with session_scope() as session:
            last_message = session.query(self.Chat)\
                .filter_by(chat_room_id=chat_room_id)\
                .order_by(desc("created_at"))\
                .first()
            if last_message == None:
                return {}
            return last_message.asdict()

    def add_message(self, chat_room_id, text, img, author_id):
        with session_scope() as session:
            chat = Chat(
                    chat_room_id=str(chat_room_id),
                    text=text,
                    img=img,
                    author_id=str(author_id),
                )
            session.add(chat)
            session.flush()
            session.refresh(chat)
            chat = chat.asdict()

            chat_room = session.query(self.ChatRoom).filter_by(id=chat_room_id).one().asdict()

            dealer_id = chat_room.get("seller_id") \
                if chat_room.get("buyer_id") == author_id \
                else chat_room.get("buyer_id")
            dealer = self.UserService().get_user(id=dealer_id)

            chat["dealer_name"] = dealer.get("full_name")
            chat["dealer_id"] = dealer.get("full_name")
            chat["created_at"] = datetime.timestamp(chat.get("created_at"))
            chat["updated_at"] = datetime.timestamp(chat.get("updated_at"))
            chat["author_name"] = self.UserService().get_user(id=chat.get("author_id")).get("full_name")
            return chat
    
    def get_conversation(self, user_id, chat_room_id):
        with session_scope() as session:
            return [
                {
                    **chat.asdict(),
                    "created_at": datetime.timestamp(chat.asdict().get("created_at")),
                    "updated_at": datetime.timestamp(chat.asdict().get("updated_at")),
                    "author_name": self.UserService().get_user(id=chat.asdict().get("author_id")).get("full_name")
                } for chat in session.query(self.Chat)\
                    .filter_by(chat_room_id=chat_room_id)
                    .order_by(asc("created_at"))
            ]


class ChatRoomService:
    def __init__(self, UserService=UserService, ChatRoom=ChatRoom, ChatService=ChatService):
        self.UserService=UserService
        self.ChatRoom = ChatRoom
        self.ChatService = ChatService

    def get_chat_rooms(self, user_id):
        rooms = []
        data = []
        with session_scope() as session:
            data = session.query(self.ChatRoom)\
            .filter(or_(self.ChatRoom.buyer_id==user_id, self.ChatRoom.seller_id==user_id))\
            .all()
            
            for chat_room in data:
                chat_room = chat_room.asdict()
                chat = self.ChatService().get_last_message(chat_room_id=chat_room.get("id"))

                author_id = chat.get("author_id", None)
                author = {} if author_id == None else self.UserService().get_user(id=author_id)

                dealer_id = chat_room.get("seller_id") \
                    if chat_room.get("buyer_id") == user_id \
                    else chat_room.get("buyer_id")
                dealer = self.UserService().get_user(id=dealer_id)
                rooms.append({
                    "author_name": author.get("full_name"),
                    "author_id": author_id,
                    "dealer_name": dealer.get("full_name"),
                    "dealer_id": dealer_id,
                    "text": chat.get("text", "Start Conversation!"),
                    "img": chat.get("img", None),
                    "created_at": datetime.timestamp(chat_room.get("created_at")),
                    "updated_at": datetime.timestamp(chat_room.get("updated_at")),
                    "chat_room_id": chat_room.get("id")
                })
        return sorted(rooms, key=itemgetter('created_at')) 


class ChatSocketService(socketio.AsyncNamespace):
    def __init__(self, namespace, sio, ChatService=ChatService, ChatRoomService=ChatRoomService):
        super().__init__(namespace)
        self.ChatService = ChatService
        self.ChatRoomService = ChatRoomService
        self.sio = sio

    async def authenticate(self, encoded_token):
        decoded_token = jwt.decode(encoded_token, APP_CONFIG.get("SANIC_JWT_SECRET"), algorithms=['HS256'])
        user_id = decoded_token.get("id")
        return user_id

    async def join_chat_rooms(self, sid, user_id):
        rooms = self.ChatRoomService().get_chat_rooms(user_id=user_id)
        for room in rooms:
            self.sio.enter_room(sid, room.get("chat_room_id"))
        return rooms

    async def on_connect(self, sid, environ):
        user_id = await self.authenticate(encoded_token=environ.get("HTTP_TOKEN"))
        rooms = await self.join_chat_rooms(sid=sid, user_id=user_id)
        await self.emit("get_chat_list", rooms)

    async def on_disconnect(self, sid):
        await self.emit("load", {"data":"success"})

    async def on_set_chat_room(self, sid, data):
        user_id = await self.authenticate(encoded_token=data.get("token"))
        conversation = self.ChatService().get_conversation(user_id=user_id, chat_room_id=data.get("chat_room_id"))
        await self.emit("get_chat_room", conversation)

    async def on_send_new_message(self, sid, data):
        user_id = await self.authenticate(encoded_token=data.get("token"))
        chat = self.ChatService().add_message(
            chat_room_id=data.get("chat_room_id"), 
            text=data.get("text"), 
            img=data.get("img"), 
            author_id=user_id)
        await self.emit("get_new_message", chat)



