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
    filtered = {k: request.json.get(k) for k in ("email", "password")}
    request.app.seller_service.create_account(**filtered)
    return json("")


async def seller_login(request):
    filtered = {k: request.json.get(k) for k in ("email", "password")}
    seller = request.app.seller_service.authenticate(**filtered)
    if seller is None:
        raise AuthenticationFailed()
    return {"id": seller["id"], "email": seller["email"]}
