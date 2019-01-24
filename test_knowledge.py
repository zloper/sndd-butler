from unittest import TestCase
import asyncio
from knowledge import Knowledge


class TestKnowledge(TestCase):
    def test_annotations(self):
        brain = Knowledge('alice ', 'bob ')

        @brain.simple('what time is it now?')
        async def current_time(message: str):
            return 'no time - no problem'

        @brain.regexp(r'I am (?P<name>\w+)')
        async def greet(message: str, name: str):
            return f"Hello, {name}!"

        @brain.simple("raise an error")
        async def broken(message: str):
            raise RuntimeError("test error")

        @brain.simple("skip none")
        async def skip_none(message: str):
            return None

        @brain.simple('multi')
        @brain.simple('another')
        @brain.regexp('.*?nano.*')
        async def multi(message: str):
            return 'ok'

        @brain.default()
        async def unknown(message: str):
            return "WTF?"

        async def main():
            assert await brain('bob what time is it now?') == 'no time - no problem', 'simple match'
            assert await brain('alice I am Brayan!') == 'Hello, Brayan!', 'regexp named match'
            assert await brain('nick I am Alice') is None, 'no trigger'
            assert await brain('alice raise an error') == 'WTF?', 'suppress exception'
            assert await brain('alice skip none') == 'WTF?', 'skip none result'
            assert await brain('bob who are you?') == 'WTF?', 'default trigger'
            assert await brain('alice multi') == 'ok', 'multi triggers over first simple'
            assert await brain('alice another') == 'ok', 'multi triggers over second simple'
            assert await brain('alice super nano multi') == 'ok', 'multi triggers over regexp'

        asyncio.get_event_loop().run_until_complete(main())

    def test_nested(self):
        alice = Knowledge('alice ')
        bob = Knowledge()

        @bob.simple("about time")
        async def touch(message: str):
            assert message == 'about time'
            return 'time is nothing'

        alice.prefix('ask bob ', bob)  # make nested knowledge

        reply = asyncio.get_event_loop().run_until_complete(alice('alice ask bob about time'))
        print("reply", reply)
        assert reply == 'time is nothing', 'nested knowledge'
