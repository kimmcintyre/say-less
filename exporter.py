from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build, Resource
import logging
import utils
import settings
from project_types.types import Table

class Exporter():

    def __init__(self, config_path: str|None, service_account_path: str|None) -> None:
        SCOPES: list[str] = ["https://www.googleapis.com/auth/spreadsheets"]
        creds: Credentials = Credentials.from_service_account_file(
            service_account_path or settings.DEFAULT_SERVICE_ACCOUNT_FILE, 
            scopes=SCOPES
        )
        self.sheets_service: Resource = build("sheets", 'v4', credentials=creds)
        configs = utils.get_configs(config_path or settings.DEFAULT_CONFIG_FILE)
        self.spreadsheet_id: str = configs["spreadsheet"]["id"]
        self.spreadsheet_name: str = configs["spreadsheet"].get("name", settings.DEFAULT_SHEET_NAME)
        self.log = logging.getLogger(self.__class__.__name__)

    def create_sheet(self, sheets_service: Resource, spreadsheet_id: str, table_data: Table) -> None:
        """ Creates a new sheet tab in a Google Sheet containing info about yesterday's videos """
        sheet = sheets_service.spreadsheets()
        sheet_title: str = table_data.sheet_title 
        
        # Create a new tab for yesterday's date
        body = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': sheet_title
                }
            }
        }]
        }
        sheet.batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body).execute()

        # Insert data into new tab
        table_out = {
            'values': [
                ['Channel_Handle', 'Video Title', 'Is Short?', 'Video Link', 'Published At'], 
            ]
        }

        for channel in table_data.channels:
            for video in channel.videos:
                row = [
                    channel.handle,
                    video.title,
                    video.is_short,
                    video.url,
                    video.published_at_str
                ]
                table_out["values"].append(row)

        sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_title}!A1",
            valueInputOption="RAW",
            body=table_out
        ).execute()

        self.log.info(f"YouTube links uploaded to '{self.spreadsheet_name}' Google Sheet under tab named '{sheet_title}'")
    
    def export_table(self, table_data: Table) -> None:
        self.create_sheet(self.sheets_service, self.spreadsheet_id, table_data)
