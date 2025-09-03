from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build, Resource
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pytz 
from googleapiclient.errors import HttpError
import json

CONFIG_FILE = "./local/configs.json"

# Setup service account and services that it can use
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/youtube"
]
SERVICE_ACCOUNT_FILE = "./local/secrets/service-account.json"

def _get_configs(filePath: str) -> tuple[str,str]:
    """ Reads the contents of the ./local/config.json file """
    spreadsheet_id: str = ""
    channel_handles: list = []
    with open(f'{filePath}') as f:
        d: dict = json.load(f)
        spreadsheet_id: str = d["spreadsheet"]["id"]
        channel_handles: str = d["channel_handles"]
    return spreadsheet_id, channel_handles

def _get_yesterday_date() -> tuple[datetime, str]:
    """ Retrieves datetime and string representation of yesterday's date """
    local_tz: pytz.tzinfo = pytz.timezone('America/New_York')
    current_date: datetime = datetime.now()
    midnight_today: datetime = datetime(current_date.year, current_date.month, current_date.day)
    midnight_today = local_tz.localize(midnight_today)
    midnight_yesterday: datetime = midnight_today - timedelta(days=1)
    return midnight_yesterday, midnight_yesterday.strftime("%Y-%m-%d")

def _get_today_date() -> datetime:
    """ Retrieves datetime and string representation of today's date """
    local_tz: pytz.tzinfo = pytz.timezone('America/New_York')
    current_date: datetime = datetime.now()
    midnight_today: datetime = datetime(current_date.year, current_date.month, current_date.day)
    midnight_today = local_tz.localize(midnight_today)
    return midnight_today

def _get_uploads_playlist_id(yt_service: Resource, channel_handle: str) -> str:
    """ Returns id of playlist for all uploads to the specified YouTube channel """
    channels = yt_service.channels()
    print(f"Retrieving uploadId for: {channel_handle}")
    result = channels.list(part="contentDetails", forHandle=channel_handle).execute()    
    return result["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def _get_shorts_playlist_id(uploadId: str) -> str:
    """ Returns the id of the playlist for all shorts for a given YouTube channel """
    return "UUSH" + uploadId[2:]

def _get_shorts_ids_from_shorts_playlist(yt_service: Resource, shortsPlaylistId: str) -> list[str]:
    """ Returns id of all videos found in the shorts playlist """
    try: 
        playlistItems = yt_service.playlistItems()
        result = playlistItems.list(
            part="contentDetails", 
            playlistId=shortsPlaylistId,
            maxResults=30,
            ).execute() 
        return [video["contentDetails"]["videoId"] for video in result["items"]]
    except HttpError:
        print("Shorts playlist not found.")
        return []
    
def _get_recent_videos_from_uploads(yt_service: Resource, uploadId: str) -> list[dict]:
    """ Returns list of details for the last 50 videos uploaded by a YouTube channel """
    videos = []
    shortsPlaylistId: str = _get_shorts_playlist_id(uploadId)
    shortsPlaylist: list[str] = _get_shorts_ids_from_shorts_playlist(yt_service, shortsPlaylistId)
    playlistItems = yt_service.playlistItems()
    result = playlistItems.list(
        part="snippet,contentDetails", 
        playlistId=uploadId,
        maxResults=50,
        ).execute()    
    for video in result["items"]:
        video_data: dict = {}
        videoId: str = video["contentDetails"]["videoId"]
        video_data["title"] = video["snippet"]["title"]
        video_data["url"] = "https://www.youtube.com/watch?v={}".format(
            video["contentDetails"]["videoId"])
        publishDateUTC: datetime = datetime.strptime(
            video["contentDetails"]["videoPublishedAt"], "%Y-%m-%dT%H:%M:%S%z"
            ).replace(tzinfo=ZoneInfo("UTC"))
        publishDateEST: datetime = publishDateUTC.astimezone(ZoneInfo("America/New_York"))
        publishDateESTStr: str = publishDateEST.strftime("%Y-%m-%d %H:%M:%S.%f")
        video_data["isShort"] = (videoId in shortsPlaylist)
        video_data["publishedAt"] = publishDateEST
        video_data["publishedAtStr"] = publishDateESTStr
        videos.append(video_data)
    return videos

def _get_yesterdays_videos(yesterdayDate: datetime, today: datetime, videos: list[dict]) -> list[dict]:
    """ Returns the list of details for videos published yesterday """
    return [video for video in videos if (video["publishedAt"] > yesterdayDate and video["publishedAt"] < today) ]

def _create_sheet(sheets_service: Resource, spreadsheet_id: str, yesterday: datetime, table_data: dict) -> None:
    """ Creates a new sheet tab in a Google Sheet containing Info about yesterday's videos """
    sheet = sheets_service.spreadsheets()
    
    # Create a new tab for today's date
    body = {
    'requests': [{
        'addSheet': {
            'properties': {
                'title': yesterday
            }
        }
    }]
    }
    sheet.batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body).execute()

    # Insert data into new tab
    table = {
        'values': [
            ['Channel_Handle', 'Video Title', 'Is Short?', 'Video Link', 'Published At'], 
        ]
    }

    for channel_handle, videos in table_data.items():
        for video in videos:
            row = [
                channel_handle,
                video["title"],
                video["isShort"],
                video["url"],
                video["publishedAtStr"]
            ]
            table["values"].append(row)

    sheet.values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{yesterday}!A1",
        valueInputOption="RAW",
        body=table
    ).execute()

def main() -> None:
    spreadsheet_id, channel_handles = _get_configs(CONFIG_FILE)
    creds: Credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    sheets_service: Resource = build("sheets", 'v4', credentials=creds)
    yt_service: Resource = build("youtube", 'v3', credentials=creds)
    yesterdayDate, yesterdayStr = _get_yesterday_date()
    today: datetime = _get_today_date()
    print(f"Retrieving videos in the date range: {yesterdayDate} to {today}")
    table_data = {}
    for handle in channel_handles:
        playlist_id: str = _get_uploads_playlist_id(yt_service, handle)
        videos_data: list[dict] = _get_recent_videos_from_uploads(yt_service, playlist_id)
        videos_data: list[dict] = _get_yesterdays_videos(yesterdayDate, today, videos_data)
        table_data[handle] = videos_data
    _create_sheet(sheets_service, spreadsheet_id, yesterdayStr, table_data)

if __name__ == "__main__":
    main()