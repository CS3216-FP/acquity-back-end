from unittest.mock import patch

from src.config import APP_CONFIG
from src.database import User, UserRequest, session_scope
from src.services import (
    ChatRoomService,
)
from tests.fixtures import (
    create_user, 
    create_chatrooms,
    create_buy_order,
    create_sell_order,
)
from tests.utils import assert_dict_in

chat_room_service = ChatRoomService(config=APP_CONFIG)


def test_create_chat_room():
    buyer = create_user("2", can_buy=False)
    seller = create_user("3", can_sell=False)
    chat_room = create_chatrooms("1", buyer_id=buyer["id"], seller_id=seller["id"])
    assert chat_room["buyer_id"] == buyer["id"]
    assert chat_room["seller_id"] == seller["id"]

def test_get_chat_rooms_seller():
    buyer = create_user("2", can_buy=True)
    seller = create_user("3", can_sell=True)
    buy_order = create_buy_order("1", user_id=str(buyer["id"]))
    sell_order = create_sell_order("2", user_id=str(seller["id"]))

    chat_room = create_chatrooms("1", buyer_id=buyer["id"], seller_id=seller["id"])
    chat_rooms = chat_room_service.get_chat_rooms(
        user_id=seller["id"],
        user_type="seller",
        is_archived=False
        )
    assert len(chat_rooms) == 1

def test_get_chat_rooms_buyer():
    buyer = create_user("2", can_buy=True)
    seller = create_user("3", can_sell=True)
    buy_order = create_buy_order("1", user_id=str(buyer["id"]))
    sell_order = create_sell_order("2", user_id=str(seller["id"]))

    chat_room = create_chatrooms("1", buyer_id=buyer["id"], seller_id=seller["id"])
    chat_rooms = chat_room_service.get_chat_rooms(
        user_id=buyer["id"],
        user_type="buyer",
        is_archived=False
        )
    assert len(chat_rooms) == 1

def test_get_archived_chat_rooms_buyer():
    buyer = create_user("2", can_buy=True)
    seller = create_user("3", can_sell=True)
    buy_order = create_buy_order("1", user_id=str(buyer["id"]))
    sell_order = create_sell_order("2", user_id=str(seller["id"]))

    chat_room = create_chatrooms("1", buyer_id=buyer["id"], seller_id=seller["id"])
    chat_rooms = chat_room_service.get_chat_rooms(
        user_id=buyer["id"],
        user_type="buyer",
        is_archived=True
        )
    assert len(chat_rooms) == 0

def test_get_archived_chat_rooms_seller():
    buyer = create_user("2", can_buy=True)
    seller = create_user("3", can_sell=True)
    buy_order = create_buy_order("1", user_id=str(buyer["id"]))
    sell_order = create_sell_order("2", user_id=str(seller["id"]))

    chat_room = create_chatrooms("1", buyer_id=buyer["id"], seller_id=seller["id"])
    chat_rooms = chat_room_service.get_chat_rooms(
        user_id=seller["id"],
        user_type="seller",
        is_archived=True
        )
    assert len(chat_rooms) == 0

def test_get_chat_rooms_outsider():
    buyer = create_user("2", can_buy=True)
    seller = create_user("3", can_sell=True)
    outsider = create_user("4", can_sell=True)
    buy_order = create_buy_order("1", user_id=str(buyer["id"]))
    sell_order = create_sell_order("2", user_id=str(seller["id"]))

    chat_room = create_chatrooms("1", buyer_id=buyer["id"], seller_id=seller["id"])
    chat_rooms = chat_room_service.get_chat_rooms(
        user_id=outsider["id"],
        user_type="seller",
        is_archived=False
        )
    assert len(chat_rooms) == 0