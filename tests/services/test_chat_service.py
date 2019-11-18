from datetime import datetime, timedelta

from src.config import APP_CONFIG
from src.services import ChatService
from tests.fixtures import (
    create_buy_order,
    create_chat,
    create_chat_room,
    create_match,
    create_offer,
    create_offer_response,
    create_sell_order,
    create_user,
    create_user_chat_room_association,
)
from tests.utils import assert_dict_in

chat_service = ChatService(config=APP_CONFIG)


# TODO refactor this mess
# - normal test for unarchived rooms (room, chats, buy_order, sell_order)
# - normal test for archived rooms
# - normal test for rooms the user is not in
# - test ordering by created_at
# - test the as_buyer, as_seller params
# - test is_revealed behavior
# - test latest_offer
# - test offer_response


def test_get_chats_by_user_id__chats():
    user = create_user("00")
    other_party = create_user("10")
    chat_room = create_chat_room("01")
    create_user_chat_room_association(
        "02", user_id=user["id"], chat_room_id=chat_room["id"], is_archived=False
    )
    create_user_chat_room_association(
        "12", user_id=other_party["id"], chat_room_id=chat_room["id"]
    )
    chat = create_chat("03", chat_room_id=chat_room["id"], author_id=user["id"])
    other_chat = create_chat(
        "13", chat_room_id=chat_room["id"], author_id=other_party["id"]
    )

    res = chat_service.get_chats_by_user_id(
        user_id=user["id"], as_buyer=True, as_seller=True
    )

    res_room = res["unarchived"][chat_room["id"]]
    assert_dict_in(chat_room, res_room)

    res_chats = res_room["chats"]
    assert {**chat, "type": "chat"} in res_chats
    assert {**other_chat, "type": "chat"} in res_chats


def test_get_chats_by_user_id__offers():
    user = create_user("00")
    other_party = create_user("10")
    chat_room = create_chat_room("01")
    create_user_chat_room_association(
        "02", user_id=user["id"], chat_room_id=chat_room["id"], is_archived=False
    )
    create_user_chat_room_association(
        "12", user_id=other_party["id"], chat_room_id=chat_room["id"]
    )
    offer = create_offer("03", chat_room_id=chat_room["id"], author_id=user["id"])
    other_offer = create_offer(
        "13", chat_room_id=chat_room["id"], author_id=other_party["id"]
    )

    res = chat_service.get_chats_by_user_id(
        user_id=user["id"], as_buyer=True, as_seller=True
    )

    res_room = res["unarchived"][chat_room["id"]]
    assert_dict_in(chat_room, res_room)

    res_chats = res_room["chats"]
    assert {**offer, "type": "offer"} in res_chats
    assert {**other_offer, "type": "offer"} in res_chats


def test_get_chats_by_user_id__offer_responses():
    user = create_user("00")
    other_party = create_user("10")
    chat_room = create_chat_room("01")
    create_user_chat_room_association(
        "02", user_id=user["id"], chat_room_id=chat_room["id"], is_archived=False
    )
    create_user_chat_room_association(
        "12", user_id=other_party["id"], chat_room_id=chat_room["id"]
    )
    offer = create_offer("03", chat_room_id=chat_room["id"], author_id=user["id"])
    resp = create_offer_response("04", offer_id=offer["id"])

    res = chat_service.get_chats_by_user_id(
        user_id=user["id"], as_buyer=True, as_seller=True
    )

    res_room = res["unarchived"][chat_room["id"]]
    assert_dict_in(chat_room, res_room)

    res_chats = res_room["chats"]
    assert {**offer, "type": "offer"} in res_chats
    assert {
        **offer,
        **resp,
        "author_id": other_party["id"],
        "is_deal_closed": False,
        "type": "offer_response",
    } in res_chats


def test_get_chats_by_user_id__offer_responses_not_in_room():
    user = create_user("00")
    other_party = create_user("10")
    chat_room = create_chat_room("01")
    create_user_chat_room_association(
        "02", user_id=user["id"], chat_room_id=chat_room["id"], is_archived=False
    )
    create_user_chat_room_association(
        "12", user_id=other_party["id"], chat_room_id=chat_room["id"]
    )
    offer = create_offer("03", chat_room_id=chat_room["id"], author_id=user["id"])
    create_offer_response("04")

    res = chat_service.get_chats_by_user_id(
        user_id=user["id"], as_buyer=True, as_seller=True
    )

    res_room = res["unarchived"][chat_room["id"]]
    assert_dict_in(chat_room, res_room)

    res_chats = res_room["chats"]
    assert {**offer, "type": "offer"} in res_chats
    assert "offer_resp" not in [c["type"] for c in res_chats]


def test_get_chats_by_user_id__archived():
    user = create_user("00")
    other_party = create_user("10")
    chat_room = create_chat_room("01")
    create_user_chat_room_association(
        "02", user_id=user["id"], chat_room_id=chat_room["id"], is_archived=True
    )
    create_user_chat_room_association(
        "12", user_id=other_party["id"], chat_room_id=chat_room["id"]
    )

    res = chat_service.get_chats_by_user_id(
        user_id=user["id"], as_buyer=True, as_seller=True
    )

    res_room = res["archived"][chat_room["id"]]
    assert_dict_in(chat_room, res_room)


def test_get_chats_by_user_id__not_in_room():
    user = create_user("00")
    create_chat_room("01")

    res = chat_service.get_chats_by_user_id(
        user_id=user["id"], as_buyer=True, as_seller=True
    )

    assert len(res["unarchived"]) == 0
    assert len(res["archived"]) == 0


def test_get_chats_by_user_id__as_buyer_seller():
    user = create_user("00")
    other_party = create_user("10")

    chat_room = create_chat_room("01")
    create_user_chat_room_association(
        "02",
        user_id=user["id"],
        chat_room_id=chat_room["id"],
        is_archived=False,
        role="BUYER",
    )
    create_user_chat_room_association(
        "12", user_id=other_party["id"], chat_room_id=chat_room["id"], role="SELLER"
    )

    chat_room2 = create_chat_room("11")
    create_user_chat_room_association(
        "22",
        user_id=user["id"],
        chat_room_id=chat_room2["id"],
        is_archived=False,
        role="SELLER",
    )
    create_user_chat_room_association(
        "32", user_id=other_party["id"], chat_room_id=chat_room2["id"], role="BUYER"
    )

    res_buyer = chat_service.get_chats_by_user_id(
        user_id=user["id"], as_buyer=True, as_seller=False
    )
    assert len(res_buyer["unarchived"]) == 1
    assert chat_room["id"] in res_buyer["unarchived"]

    res_seller = chat_service.get_chats_by_user_id(
        user_id=user["id"], as_buyer=False, as_seller=True
    )
    assert len(res_seller["unarchived"]) == 1
    assert chat_room2["id"] in res_seller["unarchived"]


def test_get_chats_by_user_id__buy_sell_order():
    user = create_user("00")
    other_party = create_user("10")

    buy_order = create_buy_order("02", user_id=user["id"])
    sell_order = create_sell_order("03", user_id=user["id"])
    match = create_match(
        "04", buy_order_id=buy_order["id"], sell_order_id=sell_order["id"]
    )

    chat_room = create_chat_room("01", match_id=match["id"])
    create_user_chat_room_association(
        "02", user_id=user["id"], chat_room_id=chat_room["id"], is_archived=False
    )
    create_user_chat_room_association(
        "12", user_id=other_party["id"], chat_room_id=chat_room["id"]
    )

    res = chat_service.get_chats_by_user_id(
        user_id=user["id"], as_buyer=True, as_seller=True
    )

    res_room = res["unarchived"][chat_room["id"]]
    assert buy_order == res_room["buy_order"]
    assert sell_order == res_room["sell_order"]


def test_get_chats_by_user_id__is_revealed():
    user = create_user("00")
    other_party = create_user("10")

    chat_room = create_chat_room("01")
    create_user_chat_room_association(
        "02",
        user_id=user["id"],
        chat_room_id=chat_room["id"],
        is_archived=False,
        is_revealed=True,
    )
    create_user_chat_room_association(
        "12",
        user_id=other_party["id"],
        chat_room_id=chat_room["id"],
        is_archived=False,
        is_revealed=False,
    )

    assert chat_service.get_chats_by_user_id(
        user_id=user["id"], as_buyer=True, as_seller=True
    )["unarchived"][chat_room["id"]]["is_revealed"]
    assert not chat_service.get_chats_by_user_id(
        user_id=other_party["id"], as_buyer=True, as_seller=True
    )["unarchived"][chat_room["id"]]["is_revealed"]


def test_get_chats_by_user_id__other_party_id():
    user = create_user("00")
    other_party = create_user("10")

    chat_room = create_chat_room("01")
    create_user_chat_room_association(
        "02", user_id=user["id"], chat_room_id=chat_room["id"], is_archived=False
    )
    create_user_chat_room_association(
        "12", user_id=other_party["id"], chat_room_id=chat_room["id"]
    )

    assert (
        chat_service.get_chats_by_user_id(
            user_id=user["id"], as_buyer=True, as_seller=True
        )["unarchived"][chat_room["id"]]["other_party_id"]
        == other_party["id"]
    )


def test_get_chats_by_user_id__created_at_sort():
    user = create_user("00")
    other_party = create_user("10")

    chat_room = create_chat_room("01")
    create_user_chat_room_association(
        "02", user_id=user["id"], chat_room_id=chat_room["id"], is_archived=False
    )
    create_user_chat_room_association(
        "12", user_id=other_party["id"], chat_room_id=chat_room["id"]
    )

    chat = create_chat(
        "03",
        chat_room_id=chat_room["id"],
        author_id=user["id"],
        created_at=datetime.now(),
    )
    offer = create_offer(
        "04",
        chat_room_id=chat_room["id"],
        author_id=user["id"],
        created_at=datetime.now() - timedelta(hours=1),
    )
    resp = create_offer_response(
        "05", offer_id=offer["id"], created_at=datetime.now() + timedelta(hours=1)
    )

    res_chats = chat_service.get_chats_by_user_id(
        user_id=user["id"], as_buyer=True, as_seller=True
    )["unarchived"][chat_room["id"]]["chats"]
    assert [r["id"] for r in res_chats] == [offer["id"], chat["id"], resp["id"]]


def test_get_chats_by_user_id__latest_offer():
    user = create_user("00")
    other_party = create_user("10")

    chat_room = create_chat_room("01")
    create_user_chat_room_association(
        "02", user_id=user["id"], chat_room_id=chat_room["id"], is_archived=False
    )
    create_user_chat_room_association(
        "12", user_id=other_party["id"], chat_room_id=chat_room["id"]
    )

    pending_offer = create_offer(
        "03", chat_room_id=chat_room["id"], author_id=user["id"], offer_status="PENDING"
    )
    create_offer(
        "04",
        chat_room_id=chat_room["id"],
        author_id=user["id"],
        offer_status="REJECTED",
    )

    assert (
        pending_offer
        == chat_service.get_chats_by_user_id(
            user_id=user["id"], as_buyer=True, as_seller=True
        )["unarchived"][chat_room["id"]]["latest_offer"]
    )
