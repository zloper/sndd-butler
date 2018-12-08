# from brain import bot
import lib
import random
import json

def get_player(server):
    return lib.players.get(server, None)

def set_player(server, value):
    lib.players[server] = value
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

    if voice_chat:
        player = set_player(message.server, await voice_chat.create_ytdl_player(url))
        player.volume = 0.5
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
