from unittest import TestCase
import asyncio
from root import root
import general


class TestJokes(TestCase):
    def test_jokes(self):
        joke = asyncio.get_event_loop().run_until_complete(root('сая скажи шутку'))
        print("Joke:", joke)
        assert joke is not None, 'get joke'
