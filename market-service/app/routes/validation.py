import re
from datetime import datetime

from app.errors.handlers import InvalidArgument


def validate_market_query(code, start, end):
    if not re.fullmatch(r"\d{6}", code or ""):
        raise InvalidArgument("code 必须是 6 位数字")

    start_date = _parse_date("start", start)
    end_date = _parse_date("end", end)
    if start_date > end_date:
        raise InvalidArgument("start 不能晚于 end")
    try:
        max_end_date = start_date.replace(year=start_date.year + 10)
    except ValueError:
        max_end_date = start_date.replace(year=start_date.year + 10, day=28)
    if end_date > max_end_date:
        raise InvalidArgument("查询日期范围不能超过 10 年")


def _parse_date(name, value):
    if not re.fullmatch(r"\d{8}", value or ""):
        raise InvalidArgument(f"{name} 必须使用 yyyyMMdd 格式")
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except ValueError as error:
        raise InvalidArgument(f"{name} 不是有效日期") from error
