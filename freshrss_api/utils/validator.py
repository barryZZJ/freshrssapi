def parse_ids(cls, v: str) -> list[int]:
    if isinstance(v, list):
        if not all(isinstance(a, str) for a in v):
            try:
                v = [int(a) for a in v]
            except Exception:
                raise ValueError
        return v

    if isinstance(v, str):
        if v == '':
            return []
        return [int(a) for a in v.split(',')]
    raise ValueError
