import aiohttp
from datetime import *

from root import root
from pyquery import PyQuery as pq
import bot_tools as bt
import git


@root.regexp("(joke|(рас)?скаж(и|те) шутк[ауи])")
async def jokes(message: str, **kwargs):
    """
    Get a random joke
    """
    async with aiohttp.ClientSession() as session:
        response = await session.get("https://bash.im/random")
        data = await response.text()
    block = pq(pq(data).find('.text')[0])
    return block.text()


@root.regexp("(help|что ты (можешь|умеешь))")
async def help(message: str, **kwargs):
    """
    Print help
    """
    import help_parser
    with open('brain.py', 'r') as f:
        txt = f.read()
    txt = help_parser.parse(txt)
    return txt


@root.regexp("(hello|привет|хаюшки|хай!|здравствуй|прив(ет|ки|етик))")
async def hello(message: str, **kwargs):
    """
    Say hello
    """
    return bt.hi_answer()


@root.regexp("(ты кто|что ты такое)")
async def who(message: str, **kwargs):
    """
    Say who am i
    """
    answr = 'Артефакт нейронной сети синедара, и по совместительству скромный дворецкий сервера сндд'
    return answr


@root.regexp("(бака)")
async def baka(message: str, **kwargs):
    """
    Say baka
    """
    return 'Я бака!? Тебя давно в мокушку не кусали?! >_<'


@root.regexp("(который час?)|(подскажи время)")
async def time(message: str, **kwargs):
    """
    Say time
    """
    msg = kwargs['raw_message']
    tm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    name = str(msg.author).split("#")[0]
    return '%s господин %s!' % (tm, name)


@root.regexp("(ты)")
async def you(message: str, **kwargs):
    """
    Say about you
    """
    return bt.you_answer()


@root.regexp("(кто в комнате?)")
async def who(message: str, **kwargs):
    """
    Say local meme
    """
    return 'Тут темно страшно и какой-то паладин лезет обниматься!'


@root.regexp("(кыкай каст)")
async def kick(message: str, **kwargs):
    """
    Say another local meme
    """
    return 'Сам кыкай %s бака!' % str(kwargs['raw_message'].author).split("#")[0]


@root.regexp("(курс валюты)")
async def er(message: str, **kwargs):
    """
    Say extended rate
    """
    message = kwargs['raw_message']
    cur = str(message.content).split('валюты')[1].strip()
    response = bt.get_current_ser(cur)
    return "Да шеф!\n %s" % response


@root.regexp("(график валюты)")
async def er(message: str, **kwargs):
    """
    Say extended rate
    """
    from bot_tools import env as env
    message = kwargs['raw_message']
    bot = kwargs['bot']
    curs = str(message.content).split('валюты')[1].strip()
    curs = curs.split(" ")
    new_rq = ""
    for cur in curs:
        response = bt.get_all_ser(cur)
        new_rq += response.strip() + "&"
    if new_rq.endswith("&"):
        new_rq = new_rq[:-1]

    try:
        with open(env.get("graph_adress", None), 'rb') as picture:
            await bot.send_file(message.channel, picture)
    except:
        print("not finde image")

    resp = bt.get_graph(new_rq)
    return "Да шеф!\n %s" % resp


@root.regexp("(какой ты версии?)|(version)")
async def vers(message: str, **kwargs):
    """
    Say say git version
    """
    gt = git.Git("")
    loginfo = gt.log()
    latest = loginfo.split("commit")[1]
    dt = latest.split("Date:")[1].split("\n")[0].strip().split(" ")
    vers = "0.1." + dt[-2][2:] + dt[1] + dt[2] + dt[3].replace(":", "") + dt[-1]
    return 'Текущая версия: %s' % vers


@root.regexp("(нужна инфа по каналу)")
async def info(message: str, **kwargs):
    """
    Say channel info
    """
    message = kwargs['raw_message']
    return 'Так точно! Сейчас все доложу!\n channel name:%s\n channel id:%s' % (
        str(message.channel), str(message.channel.id))


@root.regexp("(добавь канал в рассылку)")
async def sub(message: str, **kwargs):
    """
    Subscribe channel on Saya-news
    """
    message = kwargs['raw_message']
    if message.server == None:
        return 'Увы не могу добавить канал %s!\nПопробуйте написать в канал на сервере.' % str(message.channel)
    else:
        bt.subscribe_channel(message.server.id, message.channel.id)
        return 'Сделано!\n -- Теперь новости для этого сервера будут приходить в канал %s' % str(message.channel)


@root.regexp("(добавь канал в рабочую рассылку)")
async def sub_w(message: str, **kwargs):
    """
    Subscribe channel on work Saya-news
    """
    message = kwargs['raw_message']
    if message.server == None:
        return 'Увы не могу добавить канал %s!\nПопробуйте написать в канал на сервере.' % str(message.channel)
    else:
        bt.subscribe_work_channel(message.server.id, message.channel.id)
        return 'Сделано!\n -- Теперь рабочие новости для этого сервера будут приходить в канал %s' % str(
            message.channel)


@root.regexp("(добавь канал в тест рассылку)")
async def sub_t(message: str, **kwargs):
    """
    Subscribe channel on test Saya-news
    """
    message = kwargs['raw_message']
    if message.server == None:
        return 'Увы не могу добавить канал %s!\nПопробуйте написать в канал на сервере.' % str(message.channel)
    else:
        bt.subscribe_work_test_channel(message.server.id, message.channel.id)
        return 'Сделано!\n -- Теперь тестовые новости для этого сервера будут приходить в канал %s' % str(
            message.channel)
