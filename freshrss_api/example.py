from freshrss_api.api import FreshrssApi
from freshrss_api.utils.cache import FeedCache
from freshrss_api.utils.conf import load_conf

config = load_conf()

manager = FreshrssApi(config['username'], config['api_password'], config['api_url'])

assert manager.is_authenticated(), 'authentication failed!'

feed_cache = FeedCache()
feed_cache.load_from_api(manager)
feed_cache.dump()
feeds = feed_cache.feeds

model_unread = manager.unread_item_ids()

model_items = manager.items(with_ids=model_unread.unread_item_ids)
rssitems = model_items.items

for rssitem in rssitems:
    print(rssitem)
    feed = feeds[rssitem.feed_id]
    print(feed.title)
    print()
