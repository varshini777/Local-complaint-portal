from datetime import datetime, timezone
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

def utc_to_ist(dt):
    if dt is None:
        return None
    if not isinstance(dt, datetime):
        import logging
        logging.error(f"utc_to_ist received unexpected type: {type(dt)}")
        return ""
    # If naive, assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST)

def format_datetime(dt):
    if dt is None:
        return ""
    ist_dt = utc_to_ist(dt)
    return ist_dt.strftime("%d %b %Y, %I:%M %p")

def format_date(dt):
    if dt is None:
        return ""
    ist_dt = utc_to_ist(dt)
    return ist_dt.strftime("%d %b %Y")

def format_time(dt):
    if dt is None:
        return ""
    ist_dt = utc_to_ist(dt)
    return ist_dt.strftime("%I:%M %p")

def register_datetime_filters(app):
    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['date'] = format_date
    app.jinja_env.filters['time'] = format_time
