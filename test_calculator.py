import asyncio
from unittest import TestCase
import lib


def wait(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class TestCalculator(TestCase):
    def test_ask_if_possible(self):
        calc = lib.Calculator()
        self.assertEqual('4', wait(calc.ask_if_possible('сколько будет 2 + 2')))
        self.assertIsNone(wait(calc.ask_if_possible('нука скажи мне 8 * 2')))
        self.assertEqual('32', wait(calc.ask_if_possible('сколько будет 2**5')))
