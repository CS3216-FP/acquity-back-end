import pytest
from passlib.hash import plaintext
from sqlalchemy.orm.exc import NoResultFound

from src.database import session_scope
from src.exceptions import UnauthorizedException
from src.services import InviteService, SellerService

seller_service = SellerService(hasher=plaintext)
invite_service = InviteService()


def test_create_account():
    seller_service.create_account(
        email="a@a", password="123456", check_invitation=False
    )

    with pytest.raises(UnauthorizedException):
        seller_service.create_account(
            email="c@c", password="123456", check_invitation=True
        )

    seller_id = seller_service.authenticate(email="a@a", password="123456")["id"]
    invite_service.create_invite(origin_seller_id=seller_id, destination_email="b@b")
    seller_service.create_account(email="b@b", password="123456", check_invitation=True)


def test_authenticate():
    seller_service.create_account(
        email="a@a", password="123456", check_invitation=False
    )
    seller = seller_service.authenticate(email="a@a", password="123456")
    assert seller is not None
    assert seller["email"] == "a@a"
    assert seller["hashed_password"] == "123456"


def test_get_seller():
    seller_service.create_account(
        email="a@a", password="123456", check_invitation=False
    )
    seller_id = seller_service.authenticate(email="a@a", password="123456")["id"]

    seller_service.get_seller(id=seller_id)

    with pytest.raises(NoResultFound):
        seller_service.get_seller(id="00000000-0000-0000-0000-000000000000")
