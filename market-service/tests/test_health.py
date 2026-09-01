from app import create_app


def test_health_reports_service_is_ready():
    app = create_app({"TESTING": True})

    response = app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": {"service": "market-service", "status": "ok"}
    }
