from freshrss_api.api import FreshrssApi
from freshrss_api.utils.cache import FeedCache
from freshrss_api.utils.conf import load_conf
from freshrss_api.utils.consts import CONF, CACHE_FILE_FEEDS

config = load_conf(CONF)

manager = FreshrssApi(config['username'], config['api_password'], config['api_url'])

assert manager.is_authenticated(), 'authentication failed!'

feed_cache = FeedCache()
if CACHE_FILE_FEEDS.is_file():
    feed_cache.load_from_file(CACHE_FILE_FEEDS)
else:
    feed_cache.load_from_api(manager)
    feed_cache.dump(CACHE_FILE_FEEDS)

model_unread = manager.unread_item_ids()

model_items = manager.items(with_ids=model_unread.unread_item_ids)
rssitems = model_items.items

for rssitem in rssitems:
    print(rssitem)
    try:
        feed = feed_cache[rssitem.feed_id]
    except KeyError:
        feed_cache.update(manager)
        feed = feed_cache[rssitem.feed_id]
        feed_cache.dump(CACHE_FILE_FEEDS)

    print(feed.title)
    print()
