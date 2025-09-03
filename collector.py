from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build, Resource
from zoneinfo import ZoneInfo
from googleapiclient.errors import HttpError
from datetime import datetime
import logging
import utils
import settings
from project_types.types import Video, Table, Channel


class Collector():
    def __init__(self, config_path: str|None, service_account_path: str|None) -> None:
        SCOPES: list[str] = ["https://www.googleapis.com/auth/youtube"]
        creds: Credentials = Credentials.from_service_account_file(
            service_account_path or settings.DEFAULT_SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )
        self.yt_service: Resource = build("youtube", 'v3', credentials=creds)
        self.channel_handles = utils.get_configs(config_path or settings.DEFAULT_CONFIG_FILE)["channel_handles"]
        self.log = logging.getLogger(self.__class__.__name__)

    def _get_uploads_playlist_id(self, yt_service: Resource, channel_handle: str) -> str:
        """ Returns id of playlist for all uploads to the specified YouTube channel """
        channels = yt_service.channels()
        self.log.info(f"Retrieving uploadId for: {channel_handle}")
        result = channels.list(part="contentDetails", forHandle=channel_handle).execute()    
        return result["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def _get_shorts_playlist_id(self, uploadId: str) -> str:
        """ Returns the id of the playlist for all shorts for a given YouTube channel """
        return "UUSH" + uploadId[2:]

    def _get_shorts_ids_from_shorts_playlist(self, yt_service: Resource, shorts_playlist_id: str, max_results: int) -> list[str]:
        """ Returns id of all videos found in the shorts playlist """
        max_results = max_results or settings.DEFAULT_MAX_RESULTS
        try: 
            playlist_items = yt_service.playlistItems()
            result = playlist_items.list(
                part="contentDetails", 
                playlistId=shorts_playlist_id,
                maxResults=max_results,
                ).execute() 
            return [video["contentDetails"]["videoId"] for video in result["items"]]
        except HttpError:
            self.log.warning("Shorts playlist not found.")
            return []
        
    def _get_recent_videos_from_uploads(self, yt_service: Resource, upload_id: str, max_results: int|None) -> list[Video]:
        """ Returns list of details for the last 50 videos uploaded by a YouTube channel """
        max_results = max_results or settings.DEFAULT_MAX_RESULTS
        videos = []
        shorts_playlist_id: str = self._get_shorts_playlist_id(upload_id)
        shorts_playlist: list[str] = self._get_shorts_ids_from_shorts_playlist(yt_service, shorts_playlist_id, max_results)
        playlist_items = yt_service.playlistItems()
        result = playlist_items.list(
            part="snippet,contentDetails", 
            playlistId=upload_id,
            maxResults=max_results,
            ).execute()    
        for video in result["items"]:
            video_id = video["contentDetails"]["videoId"]
            publish_date_utc: datetime = datetime.strptime(
                video["contentDetails"]["videoPublishedAt"], "%Y-%m-%dT%H:%M:%S%z"
                ).replace(tzinfo=ZoneInfo("UTC")
                ).astimezone(ZoneInfo("America/New_York"))
            video_data: Video = Video(
                id = video["contentDetails"]["videoId"],
                title = video["snippet"]["title"],
                url = "https://www.youtube.com/watch?v={}".format(
                    video["contentDetails"]["videoId"]
                ),
                is_short = (video_id in shorts_playlist),
                published_at = publish_date_utc)
            videos.append(video_data)
        return videos

    def _get_yesterdays_videos(self, yesterdayDate: datetime, today: datetime, videos: list[Video]) -> list[Video]:
        """ Returns the list of details for videos published yesterday """
        return [video for video in videos if (video.published_at > yesterdayDate and video.published_at < today) ]
    
    def get_youtube_videos(self, max_results: int) -> Table:
        yesterdayDate: datetime = utils.get_yesterday_date()
        yesterdayDateStr: str =  utils.get_yesterday_date_string()
        todayStr: str = utils.get_today_date_string()
        today: datetime = utils.get_today_date()
        self.log.info(f"Retrieving videos in the date range: {yesterdayDateStr} to {todayStr}")
        table: Table = Table(sheet_title=utils.get_yesterday_date_string(), channels=[])
        for handle in self.channel_handles:
            channel: Channel = Channel(handle=handle, videos=[])
            playlist_id: str = self._get_uploads_playlist_id(self.yt_service, handle)
            videos_data: list[Video] = self._get_recent_videos_from_uploads(self.yt_service, playlist_id, max_results)
            videos_data: list[Video] = self._get_yesterdays_videos(yesterdayDate, today, videos_data)
            channel.add_videos(videos_data)
            table.add_channel(channel)
        return table