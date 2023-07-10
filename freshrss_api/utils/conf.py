import json
from pathlib import Path

from freshrss_api.utils.consts import CONF


def load_conf(conf: Path = CONF) -> dict:
    with conf.open('r', encoding='utf8') as f:
        return json.load(f)
