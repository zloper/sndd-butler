import aiohttp
from root import root, pushes, Push

endpoints = []


@root.prefix("узнай")
@root.prefix("тян")
@root.prefix("будь другом")
async def integrate(message: str, raw_message=None, **kwargs):
    futs = []
    channel_id = str(raw_message.channel.id)
    session_id = channel_id
    with aiohttp.ClientSession() as session:
        for url in endpoints:
            futs.append(session.post(url, data=message, headers={
                "session": session_id,
                "author": str(raw_message.author)
            }))

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
            channel_id = res.headers.get('session', '-1')
            polls.append(Push(
                channel=channel_id,
                message=message
            ))
    return polls
