from typing import NamedTuple

from knowledge import Knowledge

root = Knowledge('сая ')
scheduler = Knowledge()
pushes = Knowledge()


class Push(NamedTuple):
    server: str
    channel: str
    message: str
