import pandas as pd

from app import create_app


class FakeMarketClient:
    def __init__(self, stock_data=None, stock_error=None):
        self.stock_data = stock_data
        self.stock_error = stock_error
        self.stock_requests = []

    def get_stock_history(self, code, start, end):
        self.stock_requests.append((code, start, end))
        if self.stock_error:
            raise self.stock_error
        return self.stock_data.copy()


def test_kline_returns_frontend_compatible_candles():
    market_client = FakeMarketClient(
        stock_data=pd.DataFrame(
            [
                {"日期": "2025-01-03", "开盘": 10.2, "收盘": 10.5, "最低": 10.0, "最高": 10.8},
                {"日期": "2025-01-02", "开盘": 9.8, "收盘": 10.1, "最低": 9.7, "最高": 10.3},
            ]
        )
    )
    app = create_app({"TESTING": True}, market_client=market_client)

    response = app.test_client().get(
        "/api/kline?code=000001&start=20250101&end=20250131"
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [
            ["2025-01-02", 9.8, 10.1, 9.7, 10.3],
            ["2025-01-03", 10.2, 10.5, 10.0, 10.8],
        ]
    }
    assert market_client.stock_requests == [("000001", "20250101", "20250131")]


def test_kline_rejects_invalid_code_before_calling_market_source():
    market_client = FakeMarketClient(stock_data=pd.DataFrame())
    app = create_app({"TESTING": True}, market_client=market_client)

    response = app.test_client().get(
        "/api/kline?code=abc&start=20250101&end=20250131"
    )

    assert response.status_code == 400
    assert response.get_json()["code"] == "INVALID_ARGUMENT"
    assert market_client.stock_requests == []


def test_kline_rejects_reversed_date_range():
    market_client = FakeMarketClient(stock_data=pd.DataFrame())
    app = create_app({"TESTING": True}, market_client=market_client)

    response = app.test_client().get(
        "/api/kline?code=000001&start=20250201&end=20250101"
    )

    assert response.status_code == 400
    assert response.get_json()["code"] == "INVALID_ARGUMENT"
    assert market_client.stock_requests == []


def test_kline_maps_market_source_failure_to_bad_gateway():
    market_client = FakeMarketClient(stock_error=RuntimeError("upstream failed"))
    app = create_app({"TESTING": True}, market_client=market_client)

    response = app.test_client().get(
        "/api/kline?code=000001&start=20250101&end=20250131"
    )

    assert response.status_code == 502
    body = response.get_json()
    assert body["code"] == "MARKET_DATA_UNAVAILABLE"
    assert "upstream failed" not in body["message"]
    assert body["requestId"]


def test_kline_returns_empty_data_when_market_source_has_no_rows():
    market_client = FakeMarketClient(stock_data=pd.DataFrame())
    app = create_app({"TESTING": True}, market_client=market_client)

    response = app.test_client().get(
        "/api/kline?code=000001&start=20250101&end=20250131"
    )

    assert response.status_code == 200
    assert response.get_json() == {"data": []}


def test_kline_rejects_date_range_longer_than_ten_years():
    market_client = FakeMarketClient(stock_data=pd.DataFrame())
    app = create_app({"TESTING": True}, market_client=market_client)

    response = app.test_client().get(
        "/api/kline?code=000001&start=20150101&end=20250102"
    )

    assert response.status_code == 400
    assert response.get_json()["code"] == "INVALID_ARGUMENT"
    assert market_client.stock_requests == []
