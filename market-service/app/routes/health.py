from flask import Blueprint


health_blueprint = Blueprint("health", __name__)


@health_blueprint.get("/health")
def health():
    return {"data": {"service": "market-service", "status": "ok"}}
