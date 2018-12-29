import asyncio
from unittest import TestCase
import lib
import os

TOKEN = os.environ['TOKEN']


def wait(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class TestCryptoInfo(TestCase):
    def test_get_last_rate(self):
        info = lib.CryptoInfo(TOKEN)
        price = wait(info.get_last_rate('eth'))
        assert price is not None
        print(price)
        chart = wait(info.get_chart_last_week('eth'))
        assert chart is not None
        with open('chart.png', 'wb') as f:
            f.write(chart)

    def test_ask(self):
        info = lib.CryptoInfo(TOKEN)
        ans = wait(info.ask_if_possible('курс eth'))
        assert ans is not None
        assert isinstance(ans, str)
        ans = wait(info.ask_if_possible('график eth'))
        assert ans is not None
        assert isinstance(ans, bytes)
        ans = wait(info.ask_if_possible('some eth'))
        assert ans is None
