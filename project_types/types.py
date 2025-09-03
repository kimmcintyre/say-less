from datetime import datetime

class Video():
    def __init__(
            self, 
            id: str, 
            title: str, 
            url: str, 
            is_short: bool, 
            published_at: datetime
    ) -> None:
        self.id = id
        self.title = title
        self.url = url
        self.is_short = is_short
        self.published_at = published_at
        self.published_at_str = published_at.strftime("%Y-%m-%d %H:%M:%S.%f")
    
class Channel():
    def __init__(
        self, 
        handle: str,
        videos: list[Video]|None
    ) -> None:
        self.handle = handle
        self.videos = videos or []
    
    def add_videos(self, new_videos: list[Video]):
        self.videos.extend(new_videos)

class Table():
    def __init__(
            self, 
            sheet_title: str, 
            channels: list[Channel]|None,
    ) -> None:
        self.sheet_title = sheet_title
        self.channels = channels or []

    def add_channel(self, new_channel: Channel):
        self.channels.append(new_channel)