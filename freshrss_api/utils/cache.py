import json
from pathlib import Path

from freshrss_api.api import FreshrssApi
from freshrss_api.models import RSSFeed
from freshrss_api.utils.consts import FILE_FEEDS


class FeedCache:
    def __init__(self, ):
        self._feeds: dict[int, RSSFeed] = {}

    @property
    def feeds(self) -> dict[int, RSSFeed]:
        return self._feeds

    def __getitem__(self, feed_id: int) -> RSSFeed:
        return self._feeds[feed_id]

    def find_by_id(self, feed_id: int) -> RSSFeed:
        return self.__getitem__(feed_id)

    def update(self, manager: FreshrssApi) -> dict[int, RSSFeed]:
        return self.load_from_api(manager)

    def load_from_api(self, manager: FreshrssApi) -> dict[int, RSSFeed]:
        model = manager.feeds()
        self._feeds = {feed.feed_id: feed for feed in model.feeds}
        return self._feeds

    def load_from_file(self, feeds_file: Path = FILE_FEEDS) -> dict[int, RSSFeed]:
        with feeds_file.open('r', encoding='utf8') as f:
            feed_dicts = json.load(f)
        models = [RSSFeed.model_validate(d) for d in feed_dicts]
        self._feeds = {feed.feed_id: feed for feed in models}
        return self._feeds

    def dump(self, feeds_file: Path = FILE_FEEDS):
        feed_dicts = [feed.model_dump(mode='json')
                 for feed in self._feeds.values()]
        with feeds_file.open('w', encoding='utf8') as f:
            json.dump(feed_dicts, f, ensure_ascii=False)
