import pandas as pd


class StockService:
    REQUIRED_COLUMNS = ["日期", "开盘", "收盘", "最低", "最高"]

    def __init__(self, market_client):
        self.market_client = market_client

    def get_kline(self, code, start, end):
        frame = self.market_client.get_stock_history(code, start, end)
        if frame.empty:
            return []

        missing = set(self.REQUIRED_COLUMNS) - set(frame.columns)
        if missing:
            raise ValueError(f"股票行情缺少字段: {sorted(missing)}")

        result = frame[self.REQUIRED_COLUMNS].copy()
        result["日期"] = pd.to_datetime(result["日期"]).dt.strftime("%Y-%m-%d")
        result = result.sort_values("日期")

        return [
            [
                row["日期"],
                float(row["开盘"]),
                float(row["收盘"]),
                float(row["最低"]),
                float(row["最高"]),
            ]
            for _, row in result.iterrows()
        ]
