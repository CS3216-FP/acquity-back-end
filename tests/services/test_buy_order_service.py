from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from src.config import APP_CONFIG
from src.database import BuyOrder, Round, Security, User, session_scope
from src.exceptions import NoActiveRoundException, UnauthorizedException
from src.services import BuyOrderService
from tests.fixtures import create_buy_order, create_round, create_security, create_user
from tests.utils import assert_dict_in

buy_order_service = BuyOrderService(config=APP_CONFIG, BuyOrder=BuyOrder, User=User)


def test_get_orders_by_user():
    user_id = create_user()["id"]
    buy_order = create_buy_order("1", user_id=user_id)
    buy_order2 = create_buy_order("2", user_id=user_id)

    orders = buy_order_service.get_orders_by_user(user_id=user_id)
    assert len(orders) == 2

    assert (
        buy_order == orders[0]
        if orders[0]["number_of_shares"] == buy_order["number_of_shares"]
        else orders[1]
    )

    assert (
        buy_order2 == orders[1]
        if orders[0]["number_of_shares"] == buy_order["number_of_shares"]
        else orders[0]
    )


def test_create_order__authorized():
    user_id = create_user()["id"]
    security_id = create_security()["id"]
    round = create_round()

    buy_order_params = {
        "user_id": user_id,
        "number_of_shares": 20,
        "price": 30,
        "security_id": security_id,
    }

    with patch("src.services.RoundService.get_active", return_value=round), patch(
        "src.services.RoundService.should_round_start", return_value=False
    ):
        buy_order_id = buy_order_service.create_order(**buy_order_params)["id"]

    with session_scope() as session:
        buy_order = session.query(BuyOrder).filter_by(id=buy_order_id).one().asdict()

    assert_dict_in({**buy_order_params, "round_id": round["id"]}, buy_order)


def test_create_order__authorized_no_active_rounds():
    user_id = create_user()["id"]
    security_id = create_security()["id"]

    buy_order_params = {
        "user_id": user_id,
        "number_of_shares": 20,
        "price": 30,
        "security_id": security_id,
    }

    with patch(
        "src.services.RoundService.get_active", return_value=None
    ), pytest.raises(NoActiveRoundException):
        buy_order_id = buy_order_service.create_order(**buy_order_params)["id"]


def test_create_order__unauthorized():
    user_id = create_user(can_buy=False)["id"]
    security_id = create_security()["id"]

    with pytest.raises(UnauthorizedException):
        buy_order_service.create_order(
            user_id=user_id, number_of_shares=20, price=30, security_id=security_id
        )


def test_edit_order():
    user_id = create_user()["id"]
    buy_order = create_buy_order(user_id=user_id)

    buy_order_service.edit_order(
        id=buy_order["id"], subject_id=user_id, new_number_of_shares=50
    )

    with session_scope() as session:
        new_buy_order = (
            session.query(BuyOrder).filter_by(id=buy_order["id"]).one().asdict()
        )

    test_dict = {**buy_order, "number_of_shares": 50}
    del test_dict["updated_at"]
    assert_dict_in(test_dict, new_buy_order)


def test_delete_order():
    user_id = create_user()["id"]
    buy_order_id = create_buy_order(user_id=user_id)["id"]

    buy_order_service.delete_order(id=buy_order_id, subject_id=user_id)

    with session_scope() as session:
        assert session.query(BuyOrder).filter_by(id=buy_order_id).count() == 0
