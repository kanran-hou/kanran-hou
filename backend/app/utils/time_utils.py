from datetime import datetime, timezone, timedelta
CST = timezone(timedelta(hours=8))
def now_cst() -> datetime:
    return datetime.now(CST)
def format_cst(dt: datetime = None) -> str:
    dt = dt or now_cst()
    return dt.strftime("%Y-%m-%d %H:%M:%S")
