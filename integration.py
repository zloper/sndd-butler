import aiohttp
from root import root

endpoints = []


@root.prefix("узнай")
async def integrate(message: str, raw_message=None, **kwargs):
    futs = []
    server_id = str(raw_message.server.id) if raw_message is not None else "-1"
    with aiohttp.ClientSession() as session:
        for url in endpoints:
            futs.append(session.post(url, data=message, headers={"session": server_id}))

        for future in futs:
            res = await future
            if res.status != 200:
                continue
            return await res.text()
