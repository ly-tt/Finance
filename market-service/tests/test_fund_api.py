import math

import pandas as pd

from app import create_app


class FakeMarketClient:
    def __init__(self, value_data, return_data):
        self.value_data = value_data
        self.return_data = return_data
        self.fund_requests = []

    def get_fund_values(self, code):
        self.fund_requests.append(("value", code))
        return self.value_data.copy()

    def get_fund_returns(self, code):
        self.fund_requests.append(("return", code))
        return self.return_data.copy()


def test_fund_chart_merges_values_and_returns_with_null_for_missing_return():
    market_client = FakeMarketClient(
        value_data=pd.DataFrame(
            [
                {"净值日期": "2025-01-02", "单位净值": 1.25, "日增长率": 0.8},
                {"净值日期": "2025-01-03", "单位净值": 1.26, "日增长率": math.nan},
            ]
        ),
        return_data=pd.DataFrame(
            [{"日期": "2025-01-02", "累计收益率": 25.0}]
        ),
    )
    app = create_app({"TESTING": True}, market_client=market_client)

    response = app.test_client().get(
        "/api/fundchart?code=110022&start=20250101&end=20250131"
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [
            ["2025-01-02", 1.25, 0.8, 25.0],
            ["2025-01-03", 1.26, None, None],
        ]
    }
    assert market_client.fund_requests == [
        ("value", "110022"),
        ("return", "110022"),
    ]


def test_fund_chart_rejects_date_with_wrong_format():
    market_client = FakeMarketClient(pd.DataFrame(), pd.DataFrame())
    app = create_app({"TESTING": True}, market_client=market_client)

    response = app.test_client().get(
        "/api/fundchart?code=110022&start=2025-01-01&end=20250131"
    )

    assert response.status_code == 400
    assert response.get_json()["code"] == "INVALID_ARGUMENT"
    assert market_client.fund_requests == []


def test_fund_chart_returns_empty_data_when_no_values_exist():
    market_client = FakeMarketClient(pd.DataFrame(), pd.DataFrame())
    app = create_app({"TESTING": True}, market_client=market_client)

    response = app.test_client().get(
        "/api/fundchart?code=110022&start=20250101&end=20250131"
    )

    assert response.status_code == 200
    assert response.get_json() == {"data": []}
    assert market_client.fund_requests == [("value", "110022")]
