import aiohttp
from root import root
from pyquery import PyQuery as pq
import bot_tools as bt


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


@root.regexp("(ты)")
async def you(message: str, **kwargs):
    """
    Say abot you
    """
    return bt.you_answer()
