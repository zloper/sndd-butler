import os
import subprocess
import sys

import docker
from docker.types import Mount

from datetime import datetime, time

import requests
import lib
import random
import json
import yaml

env = {}
with open("conf.json", "r") as conf_f:
    dct = json.load(conf_f)
env.update(dct)


def get_url(str):
    str = str.strip()
    if str.startswith("https://www.youtube.com") or str.startswith("https://youtu.be"):
        str = str.split(" ")[0]
    else:
        str = None
    return str


async def reset(bot, message):
    player = set_player(message.guild, None)
    vc = bot.voice_client_in(message.guild)
    if vc:
        await bot.voice_client_in(message.guild).disconnect()
    player.voice = bot.voice_client_in(message.guild)
    return player


def get_rolles(message):
    lst = message.author.roles
    res = []
    for l in lst:
        res.append(l.name)
    return res


def get_token():
    return os.environ.get("bot_token", "")


def get_player(server):
    return lib.players.get(server, None)


def set_player(server, player):
    player_obj = lib.Player()
    player_obj.player = player
    player_obj.guild = server
    lib.players[server] = player_obj
    return lib.players[server]


async def start_song(message, bot):
    player = get_player(message.guild)
    url = str(message.content).split('спой')[1].strip()

    if url.startswith("https://www.youtube.com") or url.startswith("https://youtu.be"):
        voice_chat = bot.voice_client_in(message.guild)
    else:
        await bot.send_message(message.channel, 'Не такое спеть не могу :(')
        return

    if player != None:
        player.stop()
        player.replay = False

    if voice_chat:
        player = set_player(message.guild, await voice_chat.create_ytdl_player(url))
        player.vol(0.5)
    else:
        await bot.send_message(message.channel, 'Так меня не услышат Т_Т')
        return

    await bot.send_message(message.channel, 'Ладушки!')
    if player:
        player.start()
    else:
        await bot.send_message(message.channel, 'Так ведь это... Тишина же...')


def random_answer():
    with open("random_answers.json", "r") as f:
        answers = json.load(f)
    return random.choice(answers)


def log(txt):
    tm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_str = "[%s]: %s \n" % (str(tm), str(txt))
    with open("bot_log.log", "a") as f:
        f.write(full_str)
        print(full_str)


def you_answer():
    with open("you_answers.json", "r") as f:
        answers = json.load(f)
    return random.choice(answers)


def q_answer():
    answers = ['Вот так?',
               'Так нормально?',
               'Так пойдет?',
               'Помогло? >_<',
               'Получилось? :)']
    return random.choice(answers)


def hi_answer():
    answers = ['Приветик! ^_^',
               'Хай! =3',
               'Здравствуйте господин!',
               'Хайюшки! >_<',
               'Привет! :)']
    return random.choice(answers)


async def check_today_price(bot, current_dt):
    cur = env.get("currency_check", "GBP")
    for days_count in [14, 7]:
        answr, best_price_dt = find_best_ser(cur, days_count)
        if best_price_dt == current_dt:
            news_txt = "Согласно данным ЦБ - сегодня (%s) нас ожидает высокий курс валюты. А именно %s." \
                       "Не пропустите момент, так как это лучший курс за последние %s дней." \
                       "%s" % (str(current_dt), cur, str(days_count), str(answr))
            await send_news(bot, "Выгодный курс валюты", news_txt)
            return


async def day_common_news(bot):
    url = env.get("day_url", None)
    res = requests.get("%s/GetRandomDayInfo" % url)
    txt = res.text
    img = ""
    if "https" in res.text:
        img = "https" + txt.split('https')[1]
        txt = txt.split('https')[0]
    await send_news(bot, "История даты", txt.strip(), img=img)
    return


# TODO Fix img args
async def ask_common_news(bot, message):
    url = env.get("day_url", None)
    res = requests.get("%s/GetRandomDayInfo" % url)
    txt = res.text
    img = None
    if "https" in res.text:
        img = "https" + txt.split('https')[1]
        txt = txt.split('https')[0]
    if img is not None:
        await personal_news(bot, message.channel, "История даты", txt.strip(), img=img)
    else:
        await personal_news(bot, message.channel, "История даты", txt.strip())
    return


def get_news_chls():
    chls = Channels.news.read()
    if chls == {}:
        return None

    res = []
    for k in chls:
        res.append(chls[k])
    return res


def get_work_chls():
    return list(Channels.work.read().values())


def get_work_test_chls():
    return list(Channels.test.read().values())


async def send_news(bot, news_theme, news_text, img="https://b.radikal.ru/b38/1905/96/4ace2aef7ced.gif"):
    import news_module
    chls = get_news_chls()
    if chls is None:
        print("News not send. News channels not find.")
        return

    for id in chls:
        chl = bot.get_channel(id)
        await news_module.news_form(chl, bot, news_theme, news_text, img=img)


async def personal_news(bot, chl, news_theme, news_text, img="https://b.radikal.ru/b38/1905/96/4ace2aef7ced.gif"):
    import news_module
    await news_module.news_form(chl, bot, news_theme, news_text, img=img)


async def send_work_text(bot, text: str):
    chls = get_work_chls()
    for id in chls:
        channel = bot.get_channel(id)
        await bot.send_message(channel, text)


async def send_work_test_text(bot, text: str):
    chls = get_work_test_chls()
    for id in chls:
        channel = bot.get_channel(id)
        await bot.send_message(channel, text)


def find_best_ser(cur, days):
    """
    get best extended rates on last days
    :param cur: string - currency code (USD,GBP,...)
    :param days: days interval for review
    :return: string response and str date of best day price ('%Y-%m-%d')
    """
    url = env.get("ser_url", None)
    res = requests.get("%s/GetBestOf?cur=%s&days=%s" % (url, cur, str(days)))
    tmp_dt = res.text.split("(")[1].split(")")[0]
    best_price_dt = datetime.strptime(tmp_dt, '%d.%m.%Y').strftime('%Y-%m-%d')
    return res.text, best_price_dt


def get_current_ser(cur):
    """
    get extended rates
    :param cur: string - currency code (USD,GBP,...)
    :return: string response
    """
    url = env.get("ser_url", None)
    res = requests.get("%s/GetCurrent?cur=%s" % (url, cur))
    return res.text


def get_all_ser(cur):
    url = env.get("ser_url", None)
    res = requests.get("%s/GetAllDays?cur=%s" % (url, cur))
    return res.text


def get_graph(rq):
    url = env.get("serg_url", None)
    res = requests.get("%s/DrawER?%s" % (url, rq))
    return res.text


async def simc(name):
    c = docker.from_env()
    pathname = os.path.dirname(sys.argv[0])
    in_f = pathname + "/simc_input1.simc"
    input_file = pathname + "/simc_input.simc"
    with open(input_file, "r") as f:
        cfg = f.read()
    cfg = cfg.replace("NAMEHERE", name)
    with open(in_f, "w") as f:
        f.write(cfg)
    m = Mount("/app/SimulationCraft/workfile.simc", in_f, type="bind")

    result = c.containers.run('simulationcraftorg/simc',
                              command="./simc /app/SimulationCraft/workfile.simc",
                              remove=True,
                              mounts=[m])

    result = result.decode()
    dps = result.split("DPS Ranking:")[1].split("100.0%  Raid")[0].strip()
    hp = result.split("health=")[1].split("|")[0].strip()
    link = result.split("Origin:")[1].split("Talents:")[0].strip()
    mastery = result.split("mastery=")[1].split("|")[0].strip()
    versatility = result.split("versatility=")[1].split("|")[0].strip()
    crit = result.split("crit=")[1].split("|")[0].strip()
    haste = result.split("haste=")[1].split("|")[0].strip()

    msg = """Персонаж: %s
    Дпс: %s
    Искусность: %s Универсальность: %s Крит: %s Скорость: %s
    Здоровье: %s
    Персонаж: %s""" % (name, dps, mastery, versatility, crit, haste, hp, link)
    return msg


def get_game_info(game):
    game = game.lower().strip()
    if game == "overwatch":
        msg = """
        Статистика игр https://www.overbuff.com
        Фан: https://www.youtube.com/channel/UC02vp6CdqGfbJFF5tYc8mOw
        """
        return msg

    if game == "wow":
        msg = """
        Информация по мифик+: https://raider.io/
        Информация по рейд логам: https://www.warcraftlogs.com/
        Информация по квестам/предметам: https://ru.wowhead.com/
        Информация по дпс трейтам: https://www.herodamage.com/
        Дискорд каналы по спекам:
            Death Knight: https://discord.gg/acherus
            Demon Hunter: https://discord.gg/zGGkNGC
            Druid: https://discord.gg/dreamgrove
            Hunter: https://discord.gg/yqer4BX
            Mage: https://discord.me/alteredtime
            Monk: http://discord.gg/peakofserenity
            Paladin: https://discord.gg/0dvRDgpa5xZHFfnD
            Priest: https://discord.gg/WarcraftPriests
            Rogue: https://discord.gg/0h08tydxoNhfDVZf
            Shaman: https://discord.gg/earthshrine
            Warlock: https://discord.gg/0onXDymd9Wpc2CEu
            Warrior: https://discord.gg/0pYY7932lTH4FHW6
        Новости: https://twitter.com/warcraftdevs
        """
        return msg
    return None


def subscribe_channel(server, id):
    dct = Channels.news.read()
    dct[server] = id
    Channels.news.save(dct)


def subscribe_work_channel(server, id):
    dct = Channels.work.read()
    dct[server] = id
    Channels.work.save(dct)


def subscribe_work_test_channel(server, id):
    dct = Channels.test.read()
    dct[server] = id
    Channels.test.save(dct)


class Channel:
    def __init__(self, file_name: str):
        self.__file_name = file_name

    def read(self) -> dict:
        try:
            with open(self.__file_name, 'r') as f:
                return yaml.load(f.read())
        except FileNotFoundError:
            return {}

    def save(self, chls: dict):
        with open(self.__file_name, "w") as f:
            yaml.dump(chls, f)
            return chls


class Channels:
    work = Channel('work_channels.yaml')
    news = Channel("news_channels.yaml")
    test = Channel("test_channels.yaml")
