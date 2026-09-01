import akshare as ak

class AkshareClient:
    def get_stock_history(self, code, start, end):
        return ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start,
            end_date=end,
            adjust="qfq",
        )

    def get_fund_values(self, code):
        return ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")

    def get_fund_returns(self, code):
        return ak.fund_open_fund_info_em(
            symbol=code,
            indicator="累计收益率走势",
            period="成立来",
        )
