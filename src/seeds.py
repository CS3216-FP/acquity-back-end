from passlib.hash import argon2
import uuid
from src.database import Security, User, session_scope, ChatRoom, Chat


def seed_db():
    with session_scope() as session:
        if session.query(User).filter_by(email="a@a.com").count() == 0:
            session.add(
                User(
                    email="a@a.com",
                    hashed_password=argon2.hash("acquity"),
                    full_name="Ben",
                    can_buy=True,
                    can_sell=True,
                )
            )
        if session.query(User).filter_by(email="b@b.com").count() == 0:
            session.add(
                User(
                    email="b@b.com",
                    hashed_password=argon2.hash("acquity"),
                    full_name="Brandon",
                    can_buy=True,
                    can_sell=False,
                )
            )
        brandon_id = getattr(session.query(User).filter_by(email="b@b.com").first(), "id")
        ben_id = getattr(session.query(User).filter_by(email="a@a.com").first(), "id")
        session.add(
            ChatRoom(
                seller_id=str(ben_id),
                buyer_id=str(brandon_id),
            )
        )
        chat_room_id = getattr(session.query(ChatRoom).filter_by(seller_id=str(ben_id)).first(), "id")
        session.add(
            Chat(
                chat_room_id=str(chat_room_id),
                text="hello world",
                chat_type="text"
            )
        )
        if session.query(Security).filter_by(name="Grab").count() == 0:
            session.add(Security(name="Grab"))


if __name__ == "__main__":
    seed_db()
