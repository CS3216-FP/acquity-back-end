from sanic import Blueprint
from sanic.response import json
from sanic_jwt.decorators import inject_user, protected
from sanic_jwt.exceptions import AuthenticationFailed
from src.utils import expects_json_object
from config import client, secret, redirect_uri
from src.services import UserService
import requests

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


@blueprint.post("/user/linkedin/token")
async def retrieve_linkedin_token(request):
    code = request.json.get("code")
    token = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        headers={"Content-Type": "x-www-form-urlencoded"},
        params={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client,
            "client_secret": secret,
            }
        ).json()
    return json({"token": token})


@blueprint.post("/user/linkedin/signup")
async def create_user_linkedin(request):
    token = request.json.get("token")
    user_profile_data = requests.get(
        "https://api.linkedin.com/v2/me",
        headers={'Authorization': 'Bearer ' + token}
    ).json()
    user_email_address_data = requests.get(
        "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
        headers={'Authorization': 'Bearer ' + token}
    ).json()
    user_data = {
        "email": user_email_address_data.get("elements")[0].get("handle~").get("emailAddress"),
        "password": user_profile_data.get("id"),
        "full_name": user_profile_data.get("localizedFirstName") + " " + user_profile_data.get("localizedLastName")
    }
    user_service = UserService()
    user_service.create(**user_data)
    #ser = request.app.user_service.create(user_data)
    return json(user_data)