import aiohttp
from root import root

endpoints = []


@root.prefix("узнай")
async def integrate(message: str, **kwargs):
    futs = []
    with aiohttp.ClientSession() as session:
        for url in endpoints:
            futs.append(session.post(url, data=message))

        for future in futs:
            res = await future
            if res.status != 200:
                continue
            return await res.text()
