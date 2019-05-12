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
async def baka(message: str, **kwargs):
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
async def you(message: str, **kwargs):
    """
    Say local meme
    """
    return 'Тут темно страшно и какой-то паладин лезет обниматься!'


@root.regexp("(кто в комнате?)")
async def you(message: str, **kwargs):
    """
    Say local meme
    """
    return 'Тут темно страшно и какой-то паладин лезет обниматься!'


@root.regexp("(кыкай каст)")
async def you(message: str, **kwargs):
    """
    Say another local meme
    """
    return 'Сам кыкай %s бака!' % str(kwargs['raw_message'].author).split("#")[0]

@root.regexp("(какой ты версии?)|(version)")
async def you(message: str, **kwargs):
    """
    Say say git version
    """
    gt = git.Git("")
    loginfo = gt.log()
    latest = loginfo.split("commit")[1]
    dt = latest.split("Date:")[1].split("\n")[0].strip().split(" ")
    vers = "0.1." + dt[-2][2:] + dt[1] + dt[2] + dt[3].replace(":", "") + dt[-1]
    return 'Текущая версия: %s' % vers