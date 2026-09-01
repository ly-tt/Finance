import logging
import uuid

from flask import g, jsonify


logger = logging.getLogger(__name__)


class InvalidArgument(ValueError):
    pass


class MarketDataUnavailable(RuntimeError):
    pass


def register_error_handlers(app):
    @app.before_request
    def assign_request_id():
        g.request_id = str(uuid.uuid4())

    @app.errorhandler(InvalidArgument)
    def handle_invalid_argument(error):
        return jsonify(
            code="INVALID_ARGUMENT",
            message=str(error),
            requestId=g.request_id,
        ), 400

    @app.errorhandler(MarketDataUnavailable)
    def handle_market_data_unavailable(error):
        logger.warning("Market data request failed: %s", error)
        return jsonify(
            code="MARKET_DATA_UNAVAILABLE",
            message="行情数据暂时不可用，请稍后重试",
            requestId=g.request_id,
        ), 502
