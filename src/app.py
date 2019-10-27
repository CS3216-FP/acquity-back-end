import traceback

import socketio
from sanic import Sanic
from sanic.exceptions import SanicException
from sanic.response import json
from sanic_cors.extension import CORS as initialize_cors
from sanic_jwt import Initialize as initialize_jwt
from sanic_jwt import Responses

from src.api import blueprint, user_login
from src.chat_service import ChatSocketService
from src.config import APP_CONFIG
from src.exceptions import AcquityException
from src.services import (
    BannedPairService,
    BuyOrderService,
    ChatRoomService,
    ChatService,
    MatchService,
    RoundService,
    SecurityService,
    SellOrderService,
    SocialLogin,
    UserService,
)

app = Sanic(load_env=False)
app.config.update(APP_CONFIG)

sio = socketio.AsyncServer(async_mode="sanic", cors_allowed_origins=[])
sio.attach(app)
sio.register_namespace(ChatSocketService("/v1/chat", app.config))

app.user_service = UserService(app.config)
app.sell_order_service = SellOrderService(app.config)
app.buy_order_service = BuyOrderService(app.config)
app.security_service = SecurityService(app.config)
app.round_service = RoundService(app.config)
app.match_service = MatchService(app.config)
app.banned_pair_service = BannedPairService(app.config)
app.chat_room_service = ChatRoomService(app.config)
app.chat_service = ChatService(app.config)
app.social_login = SocialLogin(app.config, sio)

initialize_cors(app)


class AcquityJwtResponses(Responses):
    @staticmethod
    def exception_response(request, exception):
        if exception.args[0] == "Auth required.":
            # Let's throw 404 Not Found instead
            return json(
                {"error": [f"Requested URL {request.path} not found"]}, status=404
            )

        reasons = (
            exception.args[0]
            if isinstance(exception.args[0], list)
            else [exception.args[0]]
        )
        return json({"error": reasons}, status=exception.status_code)


async def retrieve_user(request, payload, *args, **kwargs):
    if payload is not None:
        return request.app.user_service.get_user(id=payload.get("id"))
    else:
        return None


initialize_jwt(
    blueprint,
    app=app,
    authenticate=user_login,
    responses_class=AcquityJwtResponses,
    retrieve_user=retrieve_user,
)

app.blueprint(blueprint)


async def error_handler(request, exception):
    if isinstance(exception, AcquityException):
        if exception.status_code == 404:
            message = f"Requested URL {request.path} not found"
        else:
            message = exception.message

        return json({"error": message}, status=exception.status_code)
    elif isinstance(exception, SanicException):
        return json({"error": exception.args}, status=exception.status_code)
    traceback.print_exc()
    return json({"error": "An internal error occured."}, status=500)


app.error_handler.add(Exception, error_handler)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config["PORT"])
