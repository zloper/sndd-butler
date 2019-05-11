from unittest import TestCase

from bot_tools import Channels


class TestChannel(TestCase):
    def test_read_save(self):
        Channels.news.save({'a': 1})
        assert 'a' in Channels.news.read()
