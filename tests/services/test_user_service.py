import pytest
from passlib.hash import plaintext
from sqlalchemy.orm.exc import NoResultFound

from src.config import APP_CONFIG
from src.database import User, session_scope
from src.exceptions import ResourceNotFoundException, UnauthorizedException
from src.services import UserService
from tests.fixtures import attributes_for_user, create_user
from tests.utils import assert_dict_in

user_service = UserService(config=APP_CONFIG, hasher=plaintext)


def test_create():
    user_service.create(email="a@a", user_id="123456", full_name="Ben", display_image=None)

    with session_scope() as session:
        users = [u.asdict() for u in session.query(User).all()]

    assert len(users) == 1
    assert_dict_in(
        {
            "email": "a@a",
            "user_id": "123456",
            "full_name": "Ben",
            "can_buy": False,
            "can_sell": False,
        },
        users[0],
    )



def test_invite_to_be_seller__unauthorized():
    inviter_id = create_user("1", is_committee=False)["id"]
    invited_id = create_user("2")["id"]

    with pytest.raises(UnauthorizedException):
        user_service.invite_to_be_seller(inviter_id=inviter_id, invited_id=invited_id)


def test_invite_to_be_seller__authorized():
    inviter_id = create_user("1", is_committee=True)["id"]
    invited_id = create_user("2")["id"]

    user_service.invite_to_be_seller(inviter_id=inviter_id, invited_id=invited_id)

    with session_scope() as session:
        assert session.query(User).get(invited_id).can_sell


def test_invite_to_be_buyer__unauthorized():
    inviter_id = create_user("1", is_committee=False)["id"]
    invited_id = create_user("2")["id"]

    with pytest.raises(UnauthorizedException):
        user_service.invite_to_be_buyer(inviter_id=inviter_id, invited_id=invited_id)


def test_invite_to_be_buyer__authorized():
    inviter_id = create_user("1", is_committee=True)["id"]
    invited_id = create_user("2")["id"]

    user_service.invite_to_be_buyer(inviter_id=inviter_id, invited_id=invited_id)

    with session_scope() as session:
        assert session.query(User).get(invited_id).can_buy
