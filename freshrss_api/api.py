from typing import Optional, Union, Literal, TypeVar

import httpx
import pydantic

from freshrss_api.utils.md5 import md5
from freshrss_api.models import *

ItemId = TypeVar('ItemId', bound=int)
ItemIdsStr = TypeVar('ItemIdsStr', bound=str)  # string joined with ','
ItemIds = Union[list[ItemId], ItemIdsStr]


class FreshrssApi:
    def __init__(self, username: str, api_password: str, api_url: Union[str, httpx.URL]):
        """api_url example: http://freshrss.example.net/api/fever.php?api"""
        self.c = httpx.Client(
            base_url=api_url,
        )
        self.api_key = self.gen_api_key(username, api_password)

    @property
    def payload(self) -> dict:
        return {'api_key': self.api_key}

    @staticmethod
    def gen_api_key(username: str, api_password: str) -> str:
        return md5(username + ':' + api_password)

    def is_connected(self) -> bool:
        resp = self.c.get('')
        try:
            resp.raise_for_status()
            RespBase.model_validate_json(resp.content)
        except (httpx.HTTPStatusError, ValueError, pydantic.ValidationError):
            return False
        return True

    def is_authenticated(self) -> bool:
        resp = self.c.post('', data=self.payload)
        try:
            resp.raise_for_status()
            RespAuthed.model_validate_json(resp.content)
        except (httpx.HTTPStatusError, ValueError, pydantic.ValidationError):
            return False
        return True

    def items(
        self,
        *,
        max_id: Optional[ItemId] = None,
        with_ids: Optional[ItemIds] = None,
        since_id: Optional[ItemId] = None,
        feed_ids: Optional[ItemIds] = None,
        group_ids: Optional[ItemIds] = None,
        limit: Literal[50] = 50,
    ) -> RespItems:
        """
        id priority: max_id > with_ids > since_id

        item count limit is 50

        note: max_id and since_id are exclusive
        """
        params = dict(
            items=None,
        )

        if sum(item is not None for item in (max_id, with_ids, since_id)) > 1:
            raise ValueError('At most one of `max_id`, `with_ids`, `since_id` can be passed!')

        if max_id is not None:
            params['max_id'] = max_id

        if with_ids is not None:
            if isinstance(with_ids, list):
                with_ids = ','.join(str(id_) for id_ in with_ids)
            params['with_ids'] = with_ids

        if since_id is not None:
            params['since_id'] = since_id

        if feed_ids is not None:
            if isinstance(feed_ids, list):
                feed_ids = ','.join(str(id_) for id_ in feed_ids)
            params['feed_ids'] = feed_ids

        if group_ids is not None:
            if isinstance(group_ids, list):
                group_ids = ','.join(str(id_) for id_ in group_ids)
            params['group_ids'] = group_ids

        resp = self.c.post('', data=self.payload, params=params)
        resp.raise_for_status()
        return RespItems.model_validate_json(resp.content)

    def feeds(self) -> RespFeeds:
        params = dict(
            feeds=None,
        )
        resp = self.c.post('', data=self.payload, params=params)
        resp.raise_for_status()
        return RespFeeds.model_validate_json(resp.content)

    def groups(self) -> RespGroups:
        params = dict(
            groups=None,
        )
        resp = self.c.post('', data=self.payload, params=params)
        resp.raise_for_status()
        return RespGroups.model_validate_json(resp.content)

    def unread_item_ids(self) -> RespUnreadItemIds:
        params = dict(
            unread_item_ids=None,
        )
        resp = self.c.post('', data=self.payload, params=params)
        resp.raise_for_status()
        return RespUnreadItemIds.model_validate_json(resp.content)

    def saved_item_ids(self) -> RespSavedItemIds:
        params = dict(
            saved_item_ids=None,
        )
        resp = self.c.post('', data=self.payload, params=params)
        resp.raise_for_status()
        return RespSavedItemIds.model_validate_json(resp.content)

    def mark(
        self,
        mark: Literal['item', 'feed', 'group'],
        as_: Literal['read', 'saved', 'unread', 'unsaved'],
        item_id: ItemId,
        *,
        before: Optional[ItemId] = None,
    ) -> Union[RespUnreadItemIds, RespSavedItemIds]:
        """default of before is 0"""
        if mark != 'item' and as_ != 'read':
            raise ValueError("`as` can only be 'read' when `mark` is 'feed' or 'group'")

        if mark == 'item' and before is not None:
            raise ValueError("`before` should only be set when `mark` is 'feed' or 'group'!")

        params = {
            'mark': mark,
            'as': as_,
            'id': item_id,
        }
        if before is not None:
            params['before'] = before
        resp = self.c.post('', data=self.payload, params=params)
        resp.raise_for_status()
        if as_ in ('read', 'unread'):
            return RespUnreadItemIds.model_validate_json(resp.content)
        else:
            return RespSavedItemIds.model_validate_json(resp.content)

    def mark_as_read(self, item_id: int) -> RespUnreadItemIds:
        return self.mark('item', 'read', item_id)

    def mark_as_unread(self, item_id: int) -> RespUnreadItemIds:
        return self.mark('item', 'unread', item_id)

    def favicons(self) -> RSSFavicon:
        params = dict(
            favicons=None,
        )
        resp = self.c.post('', data=self.payload, params=params)
        resp.raise_for_status()
        return RSSFavicon.model_validate_json(resp.content)
