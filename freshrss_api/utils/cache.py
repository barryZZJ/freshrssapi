import json
from pathlib import Path

from loguru import logger

from freshrss_api.api import FreshrssApi
from freshrss_api.models import RSSFeed


class FeedCache:
    def __init__(self, cache_file: Path, manager: FreshrssApi):
        self._feeds: dict[int, RSSFeed] = {}
        self._cache_file = cache_file
        self._manager = manager

    @property
    def feeds(self) -> dict[int, RSSFeed]:
        return self._feeds

    def __getitem__(self, feed_id: int) -> RSSFeed:
        if (feed := self._feeds.get(feed_id)) is None:
            logger.debug('local cache miss for feed {}', feed_id)
            self.load_from_api()
            self.dump()
            feed = self._feeds.get(feed_id)
            if feed is None:
                logger.error('Cannot find feed with id ' + str(feed_id))
                raise KeyError('Cannot find feed with id ' + str(feed_id))
        else:
            logger.debug('local cache hit for feed {}', feed_id)

        return feed

    def find_feed_by_id(self, feed_id: int) -> RSSFeed:
        return self.__getitem__(feed_id)

    def load_from_api(self) -> dict[int, RSSFeed]:
        model = self._manager.feeds()
        self._feeds = {feed.feed_id: feed for feed in model.feeds}
        return self._feeds

    def load_from_file(self) -> dict[int, RSSFeed]:
        with self._cache_file.open('r', encoding='utf8') as f:
            feed_dicts = json.load(f)
        models = [RSSFeed.model_validate(d) for d in feed_dicts]
        self._feeds = {feed.feed_id: feed for feed in models}
        return self._feeds

    def load(self) -> dict[int, RSSFeed]:
        """try load from file first, if fail, load from api then dump to file"""
        if self._cache_file.exists() and self._cache_file.is_file():
            logger.debug('load cache from file')
            feeds = self.load_from_file()
        else:
            logger.debug('load cache from api, and dumped to file')
            feeds = self.load_from_api()
            self.dump()
        return feeds

    def dump(self):
        feed_dicts = [feed.model_dump(mode='json', by_alias=True)
                 for feed in self._feeds.values()]
        with self._cache_file.open('w', encoding='utf8') as f:
            json.dump(feed_dicts, f, ensure_ascii=False)
