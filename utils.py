from datetime import datetime, timedelta
import pytz
import json
import settings
from jsonschema import validate


def get_configs(filePath: str) -> dict:
    """Reads the contents of the config file"""
    configs: dict = {}
    with open(f"{filePath}") as f:
        configs = json.load(f)
        validate(instance=configs, schema=settings.CONFIG_SCHEMA)
    return configs


def get_yesterday_date() -> datetime:
    """Retrieves datetime representation of yesterday's date"""
    local_tz: pytz.tzinfo = pytz.timezone("America/New_York")
    current_date: datetime = datetime.now()
    midnight_today: datetime = datetime(
        current_date.year, current_date.month, current_date.day
    )
    midnight_today = local_tz.localize(midnight_today)
    midnight_yesterday: datetime = midnight_today - timedelta(days=1)
    return midnight_yesterday


def get_yesterday_date_string() -> str:
    """Retrieves string representation of yesterday's date"""
    return get_yesterday_date().strftime("%Y-%m-%d")


def get_today_date() -> datetime:
    """Retrieves datetime and string representation of today's date"""
    local_tz: pytz.tzinfo = pytz.timezone("America/New_York")
    current_date: datetime = datetime.now()
    midnight_today: datetime = datetime(
        current_date.year, current_date.month, current_date.day
    )
    midnight_today = local_tz.localize(midnight_today)
    return midnight_today


def get_today_date_string() -> str:
    """Retrieves string representation of today's date"""
    return get_today_date().strftime("%Y-%m-%d")
