from queue import Queue
from typing import Optional
import aiohttp
import asyncio
import re

players = {}


class Player():
    server = None
    player = None
    voice = None
    replay = False
    custom_vol = 0.05

    q = Queue()
    q.put("https://www.youtube.com/watch?v=FbSNmfLrr6U")
    q.put("https://www.youtube.com/watch?v=dVR3MpmHHFc")

    def stop(self):
        if self.player != None:
            self.player.stop()
        self.player = None

    def start(self):
        self.vol(self.custom_vol)
        self.player.start()

    def vol(self, value):
        if self.player is not None:
            try:
                self.custom_vol = value
                self.player.volume = value
            except Exception as ex:
                print("Не удалось установить громкость", ex)

    async def play_r(self, bot, url):
        self.player = await self.voice.create_ytdl_player(url, after=lambda: self.repeat(bot, url))
        self.start()

    def repeat(self, bot, url):
        if self.voice and self.replay:
            asyncio.run_coroutine_threadsafe(self.play_r(bot, url), bot.loop)


class DuckDuckGo:
    PHRASES = re.compile(
        r'(что|кто|найди|инф\w*|узнай|поясни|объясни|так\w*|о|what|is|who|which|search|query|\s|the|a|есть)+(?P<query>[\w\s\d]+)$')

    async def ask(self, query: str) -> Optional[str]:
        params = {
            'q': query,
            'format': 'json',
            'kad': "ru_RU",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.duckduckgo.com/', params=params) as response:
                if response.status != 200:
                    return None
                obj = await response.json()
                return obj.get('AbstractText', None) or None  # type: Optional[str]

    async def ask_if_possible(self, query: str) -> Optional[str]:
        trig = self.trigger_word(query)
        if trig is None:
            return None

        ans = await self.ask(trig)
        return ans

    @staticmethod
    def trigger_word(text: str) -> Optional[str]:
        text = text.strip()
        for match in DuckDuckGo.PHRASES.finditer(text):
            query = match.group('query') or None
            if query is not None:
                return query
