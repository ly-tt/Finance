from flask import Flask
from flask_cors import CORS

from app.clients.akshare_client import AkshareClient
from app.config import Config
from app.errors.handlers import register_error_handlers
from app.routes.fund import fund_blueprint
from app.routes.health import health_blueprint
from app.routes.stock import stock_blueprint


def create_app(config=None, market_client=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.from_mapping(config)

    CORS(app, origins=app.config["CORS_ORIGINS"])
    app.extensions["market_client"] = market_client or AkshareClient()
    register_error_handlers(app)
    app.register_blueprint(health_blueprint)
    app.register_blueprint(stock_blueprint)
    app.register_blueprint(fund_blueprint)

    return app
