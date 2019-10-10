import datetime

import pytest
from passlib.hash import plaintext
from sqlalchemy.orm.exc import NoResultFound

from src.database import User, session_scope
from src.exceptions import UnauthorizedException
from src.services import UserService
from tests.utils import assert_dict_in

user_service = UserService(User=User, hasher=plaintext)


def test_create():
    user_service.create(email="a@a", password="123456", full_name="Ben")

    with session_scope() as session:
        users = [u.asdict() for u in session.query(User).all()]

    assert len(users) == 1
    assert_dict_in(
        {"email": "a@a", "hashed_password": "123456", "full_name": "Ben"}, users[0]
    )


def test_authenticate():
    user_params = {
        "email": "a@a",
        "hashed_password": "123456",
        "full_name": "Ben",
        "can_buy": False,
        "can_sell": False,
    }
    with session_scope() as session:
        user = User(**user_params)
        session.add(user)
        session.commit()

    user = user_service.authenticate(email="a@a", password="123456")
    assert_dict_in(user_params, user)


def test_get_user():
    with session_scope() as session:
        user = User(
            email="a@a",
            hashed_password="123456",
            full_name="Ben",
            can_buy=False,
            can_sell=False,
        )
        session.add(user)
        session.commit()

    user_id = user_service.authenticate(email="a@a", password="123456")["id"]

    user = user_service.get_user(id=user_id)
    assert_dict_in(
        {"email": "a@a", "full_name": "Ben", "can_buy": False, "can_sell": False}, user
    )

    with pytest.raises(NoResultFound):
        user_service.get_user(id="00000000-0000-0000-0000-000000000000")
