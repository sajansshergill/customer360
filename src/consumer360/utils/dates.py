from datetime import date, datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    value = value.strip()
    try:
        return datetime.fromisoformat(value.replace("Z", "")).date()
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value[:10] if fmt == "%Y-%m-%d" else value[:19], fmt).date()
        except ValueError:
            continue
    return None


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    value = str(value).strip()
    try:
        return datetime.fromisoformat(value.replace("Z", ""))
    except ValueError:
        d = parse_date(value)
        return datetime.combine(d, datetime.min.time()) if d else None
