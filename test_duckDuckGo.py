from unittest import TestCase
import lib
import asyncio


def wait(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class TestDuckDuckGo(TestCase):
    def test_ask(self):
        ddg = lib.DuckDuckGo()
        ans = asyncio.get_event_loop().run_until_complete(ddg.ask('putin'))
        assert 'Vladimir Vladimirovich' in ans

    def test_ask_if_possible(self):
        ddg = lib.DuckDuckGo()
        ans = wait(ddg.ask_if_possible('что такое - putin'))
        print(ans)
        assert ans is not None
        ans = wait(ddg.ask_if_possible('что такое putin'))
        assert ans is not None
        ans = wait(ddg.ask_if_possible('что putin'))
        assert ans is not None
        ans = wait(ddg.ask_if_possible('кто такой putin'))
        print(ans)
        assert ans is not None
        ans = wait(ddg.ask_if_possible('putin'))
        assert ans is None
