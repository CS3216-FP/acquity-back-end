from sanic import Blueprint
from sanic.response import json
from sanic_jwt.exceptions import AuthenticationFailed

from services import SellerService

blueprint = Blueprint("root", version="v1")


@blueprint.get("/")
async def root(request):
    return json({"hello": "world"})


@blueprint.post("/seller/")
async def create_seller(request):
    request.app.seller_service.create_account(**request.json)
    return json("")


async def seller_login(request):
    seller = request.app.seller_service.authenticate(**request.json)
    if seller is None:
        raise AuthenticationFailed()
    return {"id": seller["id"], "email": seller["email"]}
