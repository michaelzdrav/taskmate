from flask import current_app
import pytz
from datetime import datetime

def get_timezones():
    return {
        "Africa/Lagos": "+01:00",
        "Africa/Johannesburg": "+02:00",
        "Africa/Nairobi": "+03:00",
        "America/Buenos_Aires": "-03:00",
        "America/Chicago": "-05:00",
        "America/Los_Angeles": "-08:00",
        "America/New_York": "-04:00",
        "America/Santiago": "-04:00",
        "America/Sao_Paulo": "-03:00",
        "Asia/Dubai": "+04:00",
        "Asia/Perth": "+08:00",
        "Asia/Shanghai": "+08:00",
        "Asia/Tokyo": "+09:00",
        "Australia/Brisbane": "+10:00",
        "Australia/Melbourne": "+10:00",
        "Australia/Perth": "+08:00",
        "Australia/Sydney": "+10:00",
        "Europe/Berlin": "+02:00",
        "Europe/London": "+01:00",
        "Europe/Paris": "+02:00"
    }

def get_gmt(timezone_name):
    timezones = get_timezones()
    for key, value in timezones.items():
        current_app.logger.info("Key is %s, timezone name is %s", key, timezone_name)
        if timezone_name in key:
            return key
    return None