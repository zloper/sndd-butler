import aiohttp
from root import root, pushes, Push

endpoints = []


@root.prefix("узнай")
async def integrate(message: str, raw_message=None, **kwargs):
    futs = []
    channel_id = str(raw_message.channel.id)
    server_id = str(raw_message.server.id)
    session_id = server_id + "/" + channel_id
    with aiohttp.ClientSession() as session:
        for url in endpoints:
            futs.append(session.post(url, data=message, headers={"session": session_id}))

        for future in futs:
            res = await future
            if res.status != 200:
                continue
            return await res.text()


@pushes.simple("integration")
async def poll(*args, **kwargs):
    futs = []
    polls = []
    with aiohttp.ClientSession() as session:
        for url in endpoints:
            futs.append(session.get(url))

        for future in futs:
            res = await future
            if res.status != 200:
                continue
            message = await res.text()
            server_id, channel_id = res.headers.get('session', '-1/-1').split('/')
            polls.append(Push(
                server=server_id,
                channel=channel_id,
                message=message
            ))
    return polls
