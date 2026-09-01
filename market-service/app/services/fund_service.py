import pandas as pd


class FundService:
    VALUE_COLUMNS = ["净值日期", "单位净值", "日增长率"]

    def __init__(self, market_client):
        self.market_client = market_client

    def get_chart(self, code, start, end):
        values = self.market_client.get_fund_values(code)
        if values.empty:
            return []

        returns = self.market_client.get_fund_returns(code)

        missing = set(self.VALUE_COLUMNS) - set(values.columns)
        if missing:
            raise ValueError(f"基金净值缺少字段: {sorted(missing)}")

        date_column = "净值日期" if "净值日期" in returns.columns else "日期"
        if date_column not in returns.columns or "累计收益率" not in returns.columns:
            raise ValueError("基金累计收益率缺少日期或累计收益率字段")

        values = values[self.VALUE_COLUMNS].copy()
        values.columns = ["date", "unit_value", "pct"]
        returns = returns[[date_column, "累计收益率"]].copy()
        returns.columns = ["date", "total_return"]

        values["date"] = pd.to_datetime(values["date"]).dt.strftime("%Y-%m-%d")
        returns["date"] = pd.to_datetime(returns["date"]).dt.strftime("%Y-%m-%d")
        values["unit_value"] = pd.to_numeric(values["unit_value"], errors="coerce")
        values["pct"] = pd.to_numeric(values["pct"], errors="coerce")
        returns["total_return"] = pd.to_numeric(
            returns["total_return"], errors="coerce"
        )

        result = values.merge(returns, on="date", how="left").sort_values("date")
        start_iso = pd.to_datetime(start).strftime("%Y-%m-%d")
        end_iso = pd.to_datetime(end).strftime("%Y-%m-%d")
        result = result[(result["date"] >= start_iso) & (result["date"] <= end_iso)]

        return [
            [
                row["date"],
                _number_or_none(row["unit_value"]),
                _number_or_none(row["pct"]),
                _number_or_none(row["total_return"]),
            ]
            for _, row in result.iterrows()
        ]


def _number_or_none(value):
    return None if pd.isna(value) else float(value)
