from flask import Blueprint, current_app, jsonify, request

from app.errors.handlers import MarketDataUnavailable
from app.routes.validation import validate_market_query
from app.services.fund_service import FundService


fund_blueprint = Blueprint("fund", __name__)


@fund_blueprint.get("/api/fundchart")
def get_fund_chart():
    code = request.args.get("code")
    start = request.args.get("start")
    end = request.args.get("end")
    validate_market_query(code, start, end)

    service = FundService(current_app.extensions["market_client"])
    try:
        return jsonify(data=service.get_chart(code, start, end))
    except Exception as error:
        raise MarketDataUnavailable(str(error)) from error
