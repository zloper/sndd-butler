from typing import NamedTuple

from knowledge import Knowledge

root = Knowledge('сая ')
scheduler = Knowledge()
pushes = Knowledge()


class Push(NamedTuple):
    channel: str
    message: str
