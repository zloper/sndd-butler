import asyncio
import json
import re
from datetime import datetime, timedelta
from queue import Queue
from typing import Optional, NamedTuple, List, Union

import base64
import aiohttp

players = {}


class Player:
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


class Rate(NamedTuple):
    price: float
    timestamp: datetime


class CryptoInfo:
    PHRASES = re.compile(
        r'(?P<action>(курс|rate|динамика|chart|график)+)\s+(?P<currency>\w+)$')

    def __init__(self, token: str):
        self.token = token

    async def get_last_rate(self, currency: str) -> Optional[float]:
        start = datetime.utcnow() - timedelta(days=1)
        end = datetime.utcnow() + timedelta(days=1)
        history = await self.get_rate_history(currency, start, end)
        if history is not None and len(history) > 0:
            return history[0].price
        return 0

    async def get_chart(self, currency: str, start: datetime, end: datetime) -> Optional[bytes]:
        async with aiohttp.ClientSession() as session:
            req = json.dumps({
                "from": start.isoformat() + "Z",
                "to": end.isoformat() + "Z",
                "currency": currency,
                "token": self.token,
            })
            async with session.post('http://data.mutalk.net/crypto/chart', data=req,
                                    headers={'Content-Type': 'application/json'}) as response:
                if response.status != 200:
                    return None
                ans = await response.json()
                if ans is None:
                    return None
                return base64.decodebytes(ans.encode())

    async def get_chart_last_week(self, currency) -> Optional[bytearray]:
        start = datetime.utcnow() - timedelta(days=7)
        end = datetime.utcnow()
        return await self.get_chart(currency, start, end)

    async def get_rate_history(self, currency: str, start: datetime, end: datetime) -> Optional[List[Rate]]:
        async with aiohttp.ClientSession() as session:
            req = json.dumps({
                "from": start.isoformat() + "Z",
                "to": end.isoformat() + "Z",
                "currency": currency,
                "token": self.token,
            })
            async with session.post('http://data.mutalk.net/crypto/history', data=req,
                                    headers={'Content-Type': 'application/json'}) as response:
                if response.status != 200:
                    return None
                ans = await response.json()

                return [Rate(x['price'], datetime.utcfromtimestamp(x['timestamp'])) for x in ans]

    async def ask_if_possible(self, text: str) -> Optional[Union[str, bytearray]]:
        for match in CryptoInfo.PHRASES.finditer(text):
            currency = match.group('currency') or None
            action = match.group('action') or None
            if currency is None or action is None:
                return None
            if 'rate' in action or 'курс' in action:
                rate = await self.get_last_rate(currency)
                if rate is None:
                    return None
                return f'насколько я знаю, сейчас один {currency} стоит ${rate}'
            else:
                return await self.get_chart_last_week(currency)
