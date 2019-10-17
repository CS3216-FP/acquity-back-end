from datetime import datetime, timedelta

from src.database import (
    BuyOrder,
    Match,
    Round,
    Security,
    SellOrder,
    User,
    session_scope,
)


def attributes_for_user(id="", **kwargs):
    return {
        "email": f"a{id}@a",
        "hashed_password": f"abcdef{id}",
        "full_name": f"a{id}",
        "can_buy": True,
        "can_sell": True,
        **kwargs,
    }


def attributes_for_security(id="", **kwargs):
    return {"name": f"a{id}", **kwargs}


def attributes_for_sell_order(id=0, **kwargs):
    return {"number_of_shares": 20 + int(id), "price": 30 + int(id), **kwargs}


def attributes_for_buy_order(id=0, **kwargs):
    return {"number_of_shares": 20 + int(id), "price": 30 + int(id), **kwargs}


def attributes_for_match(id=0, **kwargs):
    return {"number_of_shares": 20 + int(id), "price": 30 + int(id), **kwargs}


def attributes_for_round(id=0, **kwargs):
    return {
        "end_time": datetime.now() + timedelta(days=1 + int(id)),
        "is_concluded": False,
        **kwargs,
    }


def create_user(id="", **kwargs):
    with session_scope() as session:
        user = User(**attributes_for_user(id, **kwargs))
        session.add(user)
        session.commit()
        return user.asdict()


def create_security(id="", **kwargs):
    with session_scope() as session:
        security = Security(**attributes_for_security(id, **kwargs))
        session.add(security)
        session.commit()
        return security.asdict()


def create_sell_order(id=0, **kwargs):
    with session_scope() as session:
        sell_order = SellOrder(
            user_id=create_user(id, **kwargs)["id"],
            security_id=create_security(id, **kwargs)["id"],
            round_id=create_round(id, **kwargs)["id"],
            **attributes_for_sell_order(id, **kwargs),
        )
        session.add(sell_order)
        session.commit()
        return sell_order.asdict()


def create_buy_order(id=0, **kwargs):
    with session_scope() as session:
        buy_order = BuyOrder(
            user_id=create_user(id, **kwargs)["id"],
            security_id=create_security(id, **kwargs)["id"],
            round_id=create_round(id, **kwargs)["id"],
            **attributes_for_buy_order(id, **kwargs),
        )
        session.add(buy_order)
        session.commit()
        return buy_order.asdict()


def create_match(id=0, **kwargs):
    with session_scope() as session:
        match = Match(
            buy_order_id=create_buy_order(id, **kwargs)["id"],
            sell_order_Id=create_sell_order(id, **kwargs)["id"],
            **attributes_for_match(id, **kwargs),
        )
        session.add(match)
        session.commit()
        return match.asdict()


def create_round(id=0, **kwargs):
    with session_scope() as session:
        round = Round(**attributes_for_round(id, **kwargs))
        session.add(round)
        session.commit()
        return round.asdict()
