from flask import Blueprint, current_app, jsonify, request

from app.errors.handlers import MarketDataUnavailable
from app.routes.validation import validate_market_query
from app.services.stock_service import StockService


stock_blueprint = Blueprint("stock", __name__)


@stock_blueprint.get("/api/kline")
def get_kline():
    code = request.args.get("code")
    start = request.args.get("start")
    end = request.args.get("end")
    validate_market_query(code, start, end)

    service = StockService(current_app.extensions["market_client"])
    try:
        return jsonify(data=service.get_kline(code, start, end))
    except Exception as error:
        raise MarketDataUnavailable(str(error)) from error
