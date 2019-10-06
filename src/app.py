from sanic import Sanic
from sanic_cors.extension import CORS

from api import blueprint
from config import APP_CONFIG

app = Sanic(load_env=False)
app.config.update(APP_CONFIG)

app.blueprint(blueprint)
CORS(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config["PORT"])
