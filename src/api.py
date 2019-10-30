from functools import wraps

from sanic import Blueprint, response
from sanic.response import json
from sanic_jwt.exceptions import AuthenticationFailed

from src.utils import expects_json_object

blueprint = Blueprint("root", version="v1")


def auth_required(f):
    @wraps(f)
    async def decorated_function(request, *args, **kwargs):
        def get_token(header):
            PREFIX = "Bearer "
            if not header.startswith(PREFIX):
                raise ValueError("Invalid token")
            return header[len(PREFIX) :]

        token = get_token(request.headers["Authorization"])
        linkedin_user = request.app.social_login.get_linkedin_user(token=token)
        user = request.app.user_service.get_user_by_linkedin_id(
            user_id=linkedin_user.get("user_id")
        )
        if user is not None:
            response = await f(request, user, *args, **kwargs)
            return response
        else:
            return json({"status": "not_authorized"}, 403)

    return decorated_function


@blueprint.get("/auth/me")
@auth_required
async def test(request, user):
    user = request.app.user_service.get_user_by_linkedin_id(user_id=user.get("user_id"))
    return json({"me": user})


@blueprint.get("/")
async def root(request):
    return json({"hello": "world"})


@blueprint.post("/user/")
@expects_json_object
async def create_user(request):
    user = request.app.user_service.create(**request.json)
    return json(user)


@expects_json_object
async def user_login(request):
    print(request)
    user = request.app.user_service.authenticate(**request.json)
    if user is None:
        raise AuthenticationFailed()
    return {"id": user["id"]}


@blueprint.post("/user/invite/seller")
@auth_required
@expects_json_object
async def invite_seller(request, user):
    return json(
        request.app.user_service.invite_to_be_seller(
            **request.json, inviter_id=user["id"]
        )
    )


@blueprint.post("/user/invite/buyer")
@auth_required
@expects_json_object
async def invite_buyer(request, user):
    return json(
        request.app.user_service.invite_to_be_buyer(
            **request.json, inviter_id=user["id"]
        )
    )


@blueprint.get("/sell_order/")
@auth_required
async def get_sell_orders_by_user(request, user):
    return json(request.app.sell_order_service.get_orders_by_user(user_id=user["id"]))


@blueprint.get("/sell_order/<id>")
@auth_required
async def get_sell_order_by_id(request, user, id):
    return json(
        request.app.sell_order_service.get_order_by_id(id=id, user_id=user["id"])
    )


@blueprint.post("/sell_order/")
@auth_required
@expects_json_object
async def create_sell_order(request, user):
    return json(
        request.app.sell_order_service.create_order(**request.json, user_id=user["id"])
    )


@blueprint.patch("/sell_order/<id>")
@auth_required
@expects_json_object
async def edit_sell_order(request, user, id):
    return json(
        request.app.sell_order_service.edit_order(
            **request.json, id=id, subject_id=user["id"]
        )
    )


@blueprint.delete("/sell_order/<id>")
@auth_required
async def delete_sell_order(request, user, id):
    return json(
        request.app.sell_order_service.delete_order(id=id, subject_id=user["id"])
    )


@blueprint.get("/buy_order/")
@auth_required
async def get_buy_orders_by_user(request, user):
    return json(request.app.buy_order_service.get_orders_by_user(user_id=user["id"]))


@blueprint.get("/buy_order/<id>")
@auth_required
async def get_buy_order_by_id(request, user, id):
    return json(
        request.app.buy_order_service.get_order_by_id(id=id, user_id=user["id"])
    )


@blueprint.post("/buy_order/")
@auth_required
@expects_json_object
async def create_buy_order(request, user):
    return json(
        request.app.buy_order_service.create_order(**request.json, user_id=user["id"])
    )


@blueprint.patch("/buy_order/<id>")
@auth_required
@expects_json_object
async def edit_buy_order(request, user, id):
    return json(
        request.app.buy_order_service.edit_order(
            **request.json, id=id, subject_id=user["id"]
        )
    )


@blueprint.delete("/buy_order/<id>")
@auth_required
async def delete_buy_order(request, user, id):
    return json(
        request.app.buy_order_service.delete_order(id=id, subject_id=user["id"])
    )


@blueprint.get("/security/")
async def get_all_securities(request):
    return json(request.app.security_service.get_all())


@blueprint.patch("/security/<id>")
@auth_required
async def edit_security_market_price(request, user, id):
    return json(
        request.app.edit_market_price(**request.json, id=id, subject_id=user["id"])
    )


@blueprint.get("/round/")
async def get_all_rounds(request):
    return json(request.app.round_service.get_all())


@blueprint.get("/round/active")
async def get_active_round(request):
    return json(request.app.round_service.get_active())


@blueprint.post("/ban/")
@auth_required
@expects_json_object
async def ban_user(request, user):
    return json(
        request.app.banned_pair_service.ban_user(**request.json, my_user_id=user["id"])
    )


@blueprint.get("/linkedin/auth")
async def linkedin_auth(request):
    socket_id = request.args.get("socketId")
    url = request.app.social_login.get_auth_url(socket_id)
    return response.redirect(url)


@blueprint.get("/linkedin/auth/callback")
async def linkedin_auth(request):
    code = request.args.get("code")
    state = request.args.get("state")
    await request.app.social_login.authenticate(code=code, socket_id=state)
    return json({"data": "success"})
