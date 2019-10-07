import datetime

import pytest
from passlib.hash import plaintext
from sqlalchemy.orm.exc import NoResultFound

from src.database import Invite, Seller, session_scope
from src.exceptions import UnauthorizedException
from src.services import SellerService

seller_service = SellerService(Seller=Seller, hasher=plaintext)


def test_create_account_no_check_invitation():
    seller_service.create_account(
        email="a@a", password="123456", check_invitation=False
    )


def test_create_account_check_invitation_unauthorized():
    with pytest.raises(UnauthorizedException):
        seller_service.create_account(
            email="c@c", password="123456", check_invitation=True
        )


def test_create_account_check_invitation_authorized():
    with session_scope() as session:
        seller = Seller(email="a@a", hashed_password="123456")
        session.add(seller)
        session.commit()

        invite = Invite(
            origin_seller_id=str(seller.id),
            destination_email="b@b",
            valid=True,
            expiry_time=datetime.datetime.now() + datetime.timedelta(days=1),
        )
        session.add(invite)

    seller_service.create_account(email="b@b", password="123456", check_invitation=True)

    with session_scope() as session:
        session.query(Seller).filter_by(email="b@b", hashed_password="123456").one()


def test_authenticate():
    with session_scope() as session:
        seller = Seller(email="a@a", hashed_password="123456")
        session.add(seller)
        session.commit()

    seller = seller_service.authenticate(email="a@a", password="123456")
    assert seller is not None
    assert seller["email"] == "a@a"
    assert seller["hashed_password"] == "123456"


def test_get_seller():
    with session_scope() as session:
        seller = Seller(email="a@a", hashed_password="123456")
        session.add(seller)
        session.commit()

    seller_id = seller_service.authenticate(email="a@a", password="123456")["id"]

    seller = seller_service.get_seller(id=seller_id)
    assert seller["email"] == "a@a"
    assert seller["hashed_password"] == "123456"

    with pytest.raises(NoResultFound):
        seller_service.get_seller(id="00000000-0000-0000-0000-000000000000")
