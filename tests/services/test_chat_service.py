from datetime import datetime, timedelta

from src.config import APP_CONFIG
from src.services import ChatService
from tests.fixtures import (
    create_archived_chat_room,
    create_chat,
    create_chat_room,
    create_offer,
    create_user,
)
from tests.utils import assert_dict_in

chat_service = ChatService(config=APP_CONFIG)


def test_get_chats_by_user_id():
    me = create_user()
    chat_room1 = create_chat_room("1", buyer_id=me["id"], is_buyer_revealed=False)
    chat_room2 = create_chat_room("2", seller_id=me["id"], is_seller_revealed=True)
    create_chat_room("127")

    archived_chat_room = create_chat_room(
        "3", seller_id=me["id"], is_seller_revealed=False
    )
    create_archived_chat_room(chat_room_id=archived_chat_room["id"], user_id=me["id"])

    chat_room1["is_revealed"] = False
    chat_room2["is_revealed"] = True
    archived_chat_room["is_revealed"] = False
    for r in [chat_room1, chat_room2, archived_chat_room]:
        r.pop("is_buyer_revealed")
        r.pop("is_seller_revealed")

    chat_room1_chat1 = create_chat(
        "x",
        chat_room_id=chat_room1["id"],
        author_id=me["id"],
        created_at=datetime.now() + timedelta(hours=2),
    )
    chat_room1_chat2 = create_chat(
        "4",
        chat_room_id=chat_room1["id"],
        author_id=chat_room1["seller_id"],
        created_at=datetime.now() + timedelta(hours=3),
    )
    chat_room1_offer = create_offer(
        "5",
        chat_room_id=chat_room1["id"],
        author_id=me["id"],
        created_at=datetime.now() + timedelta(hours=1),
    )
    chat_room2_chat1 = create_chat(
        "6",
        chat_room_id=chat_room2["id"],
        author_id=me["id"],
        created_at=datetime.now() + timedelta(hours=2),
    )
    chat_room2_chat2 = create_chat(
        "7",
        chat_room_id=chat_room2["id"],
        author_id=chat_room2["buyer_id"],
        created_at=datetime.now() + timedelta(hours=3),
    )
    chat_room2_offer = create_offer(
        "8",
        chat_room_id=chat_room2["id"],
        author_id=me["id"],
        created_at=datetime.now() + timedelta(hours=1),
    )
    archived_chat_room_chat1 = create_chat(
        "9",
        chat_room_id=archived_chat_room["id"],
        author_id=me["id"],
        created_at=datetime.now() + timedelta(hours=2),
    )
    archived_chat_room_chat2 = create_chat(
        "315",
        chat_room_id=archived_chat_room["id"],
        author_id=archived_chat_room["buyer_id"],
        created_at=datetime.now() + timedelta(hours=3),
    )
    archived_chat_room_offer = create_offer(
        "203",
        chat_room_id=archived_chat_room["id"],
        author_id=me["id"],
        created_at=datetime.now() + timedelta(hours=1),
    )

    res = chat_service.get_chats_by_user_id(user_id=me["id"])

    assert len(res["archived"]) == 1
    res_archived_chat_room = res["archived"][0]
    assert_dict_in(archived_chat_room, res_archived_chat_room)
    res_archived_chat_room_chats = res_archived_chat_room["chats"]
    assert_dict_in(archived_chat_room_offer, res_archived_chat_room_chats[0])
    assert_dict_in(archived_chat_room_chat1, res_archived_chat_room_chats[1])
    assert_dict_in(archived_chat_room_chat2, res_archived_chat_room_chats[2])

    assert len(res["unarchived"]) == 2
    unarchived_chat_rooms = res["unarchived"]

    assert_dict_in(chat_room2, unarchived_chat_rooms[0])
    res_chat_room2_chats = unarchived_chat_rooms[0]["chats"]
    assert_dict_in(chat_room2_offer, res_chat_room2_chats[0])
    assert_dict_in(chat_room2_chat1, res_chat_room2_chats[1])
    assert_dict_in(chat_room2_chat2, res_chat_room2_chats[2])

    assert_dict_in(chat_room1, unarchived_chat_rooms[1])
    res_chat_room1_chats = unarchived_chat_rooms[1]["chats"]
    assert_dict_in(chat_room1_offer, res_chat_room1_chats[0])
    assert_dict_in(chat_room1_chat1, res_chat_room1_chats[1])
    assert_dict_in(chat_room1_chat2, res_chat_room1_chats[2])
