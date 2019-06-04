from typing import NamedTuple

from knowledge import Knowledge

root = Knowledge('сая ', 'сая-чан ', 'саятян ', 'сая-тян ')
scheduler = Knowledge()
pushes = Knowledge()


class Push(NamedTuple):
    channel: str
    message: str
