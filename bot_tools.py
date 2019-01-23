import os

from datetime import datetime, time

import lib
import random
import json


def get_url(str):
    str = str.strip()
    if str.startswith("https://www.youtube.com") or str.startswith("https://youtu.be"):
        str = str.split(" ")[0]
    else:
        str = None
    return str


async def reset(bot, message):
    player = set_player(message.server, None)
    vc = bot.voice_client_in(message.server)
    if vc:
        await bot.voice_client_in(message.server).disconnect()
    player.voice = bot.voice_client_in(message.server)
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
    player_obj.server = server
    lib.players[server] = player_obj
    return lib.players[server]


async def start_song(message, bot):
    player = get_player(message.server)
    url = str(message.content).split('спой')[1].strip()

    if url.startswith("https://www.youtube.com") or url.startswith("https://youtu.be"):
        voice_chat = bot.voice_client_in(message.server)
    else:
        await bot.send_message(message.channel, 'Не такое спеть не могу :(')
        return

    if player != None:
        player.stop()
        player.replay = False

    if voice_chat:
        player = set_player(message.server, await voice_chat.create_ytdl_player(url))
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
