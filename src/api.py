from sanic import Blueprint
from sanic.response import json
from sanic_jwt.decorators import inject_user, protected
from sanic_jwt.exceptions import AuthenticationFailed

from src.utils import expects_json_object

blueprint = Blueprint("root", version="v1")


def auth_required(func):
    return (inject_user(blueprint))(protected(blueprint)(func))


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
    user = request.app.user_service.authenticate(**request.json)
    if user is None:
        raise AuthenticationFailed()
    return {"id": user["id"]}


@blueprint.post("/invite/")
@auth_required
@expects_json_object
async def create_invite(request, user):
    return json(
        request.app.user_service.invite_to_be_seller(
            **request.json, inviter_id=user["id"]
        )
    )


@blueprint.get("/sell_order/")
@auth_required
async def get_sell_orders_by_user(request, user):
    return json(request.app.sell_order_service.get_orders_by_user(user_id=user["id"]))


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
        request.app.sell_order_service.edit_order(
            **request.json, id=id, subject_id=user["id"]
        )
    )


@blueprint.get("/security/")
@protected(blueprint)
async def get_all_securities(request):
    return json(request.app.security_service.get_all())


@blueprint.post("/user/linkedin/")
@auth_required
async def create_user_linkedin(request, user):
    user_data = request.app.linkedin_service.get_user_data(**request.json)
    request.app.linkedin_service.is_email_matching(
        **{"user_email": user.get("email"), "linkedin_email": user_data.get("email")}
    )
    user_id = {
        "user_id": request.app.user_service.get_user_by_email(**user_data).get("id")
    }
    user_data_buyer_privileges = request.app.user_service.activate_buy_privileges(
        **user_id
    )
    return json(user_data_buyer_privileges)
