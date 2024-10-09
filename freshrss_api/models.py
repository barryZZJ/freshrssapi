import datetime

from pydantic import BaseModel, field_validator, Field, HttpUrl

from freshrss_api.utils.validator import parse_ids


class RSSItem(BaseModel):
    item_id: int = Field(..., alias='id')
    feed_id: int
    title: str
    author: str
    rich_content: str = Field(..., alias='html')
    url: HttpUrl
    is_saved: bool
    is_read: bool
    created_on_time: datetime.datetime

    def __str__(self):
        return ', '.join(f'{k}:{v}' for k, v in self.model_dump())


class RSSFeed(BaseModel):
    feed_id: int = Field(..., alias='id')
    favicon_id: int
    title: str
    freshrss_url: HttpUrl = Field(..., alias='url')
    site_url: HttpUrl
    is_spark: bool
    last_updated_on_time: datetime.datetime


class RSSGroup(BaseModel):
    group_id: int = Field(..., alias='id')
    title: str


class RSSFeedGroup(BaseModel):
    group_id: int
    feed_ids: list[int]

    # validators
    normalize_ids = field_validator('feed_ids', mode='before')(parse_ids)


class RSSFavicon(BaseModel):
    feed_id: int = Field(alias='id')
    data: str


class RespBase(BaseModel):
    api_version: int
    auth: bool


class RespAuthed(RespBase):
    last_refreshed_on_time: datetime.datetime

    @field_validator('auth')
    def is_authed(cls, v):
        assert v, 'Authentication field is false!'
        return v


class RespItems(RespAuthed):
    total_items: int
    items: list[RSSItem]


class RespFeeds(RespAuthed):
    feeds: list[RSSFeed]


class RespGroups(RespAuthed):
    groups: list[RSSGroup]
    """group id and group title"""
    feeds_groups: list[RSSFeedGroup]
    """feed ids of which belongs to some group"""


class RespUnreadItemIds(RespAuthed):
    unread_item_ids: list[int]

    # validators
    _normalize_ids = field_validator('unread_item_ids', mode='before')(parse_ids)


class RespSavedItemIds(RespAuthed):
    saved_item_ids: list[int]

    # validators
    _normalize_ids = field_validator('saved_item_ids', mode='before')(parse_ids)


class RespFavicons(RespAuthed):
    favicons: list[RSSFavicon]
