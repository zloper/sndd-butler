import aiohttp
from root import root
from pyquery import PyQuery as pq


@root.regexp("(joke|(рас)?скаж(и|те) шутк[ауи])")
async def jokes(message: str):
    """
    Get a random joke
    """
    async with aiohttp.ClientSession() as session:
        response = await session.get("https://bash.im/random")
        data = await response.text()
    block = pq(pq(data).find('.text')[0])
    return block.text()


