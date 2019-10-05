import os

from sanic import Sanic
from sanic.response import json
from sqlalchemy import create_engine

from database import Base

app = Sanic(load_env=False)
app.config.update(
    {
        "DATABASE_URL": os.getenv(
            "DATABASE_URL", "postgresql://acquity:acquity@localhost:5432/acquity"
        )
    }
)

database_engine = create_engine(app.config["DATABASE_URL"])
Base.metadata.create_all(database_engine)


@app.route("/")
async def test(request):
    return json({"hello": "world"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT", 8000))
