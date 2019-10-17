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


def combine_dicts(original, default_boxed):
    res = original.copy()
    for k, box_value in default_boxed.items():
        if k not in original:
            res[k] = box_value()

    return res


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
            **combine_dicts(
                attributes_for_sell_order(id, **kwargs),
                {
                    "user_id": lambda: create_user(id)["id"],
                    "security_id": lambda: create_security(id)["id"],
                    "round_id": lambda: create_round(id)["id"],
                },
            )
        )

        session.add(sell_order)
        session.commit()
        return sell_order.asdict()


def create_buy_order(id=0, **kwargs):
    with session_scope() as session:
        buy_order = BuyOrder(
            **combine_dicts(
                attributes_for_buy_order(id, **kwargs),
                {
                    "user_id": lambda: create_user(id)["id"],
                    "security_id": lambda: create_security(id)["id"],
                    "round_id": lambda: create_round(id)["id"],
                },
            )
        )

        session.add(buy_order)
        session.commit()
        return buy_order.asdict()


def create_match(id=0, **kwargs):
    with session_scope() as session:
        match = Match(
            **combine_dicts(
                attributes_for_match(id, **kwargs),
                {
                    "buy_order_id": lambda: create_buy_order(id)["id"],
                    "sell_order_id": lambda: create_sell_order(id)["id"],
                },
            )
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
