from typing import Optional
import aiohttp

player = None


# class Audio():
#     player = None
#
#     def player_stop(self):
#         self.player.stop()
#         self.player = None


class DuckDuckGo:
    PHRASES = {
        'что такое', 'кто так', 'кто так', 'найди', 'инфа', 'инфу о',
        'объясни', 'поясни', 'узнай',
        'what is', 'who is', 'which is',
        'search', 'query'
    }

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
                return obj.get('AbstractText', None)  # type: Optional[str]

    async def ask_if_possible(self, query: str) -> Optional[str]:
        trig = self.trigger_word(query)
        if trig is None:
            return None

        ans = await self.ask(trig)
        return ans

    @staticmethod
    def trigger_word(text: str) -> Optional[str]:
        text = text.strip()
        for ph in DuckDuckGo.PHRASES:
            if text.startswith(ph):
                # find next word
                parts = text[len(ph):].split(None, 1)
                if len(parts) < 2:
                    return None
                return parts[1]
