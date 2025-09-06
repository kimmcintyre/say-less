import logging
from jsonschema import validate

DEFAULT_CONFIG_FILE = "./local/configs.json"
DEFAULT_SERVICE_ACCOUNT_FILE = "./local/secrets/service-account.json"
DEFAULT_LOGGING_LEVEL = logging.INFO
DEFAULT_MAX_RESULTS = 50
DEFAULT_SHEET_NAME = "Name Not Found"
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "spreadsheet": {
            "type": "object",
            "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
            "required": ["id"],
        },
        "channel_handles": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["spreadsheet", "channel_handles"],
}
