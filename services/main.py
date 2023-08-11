import sys
import datetime
from flask import Flask, Blueprint
from flask_restx import Api
from database import engine, Base
from configs.env import ROOT_PATH_API
from dotenv import load_dotenv

load_dotenv()

from configs.env import FLASK_HOST, FLASK_PORT
from profile_controller import api as profile_ns

app = Flask(__name__)

Base.metadata.create_all(engine)

blueprint = Blueprint("api", __name__, url_prefix=ROOT_PATH_API)
api = Api(
    blueprint,
    title="Hackathon API",
    version="1.0",
    description="Hackathon API",
)

api.add_namespace(profile_ns)
app.register_blueprint(blueprint)

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
