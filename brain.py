import re
from datetime import datetime, time
from io import BytesIO
from time import sleep

import cinema_game
import helper
import q_module
import discord
import sys
import json
import bot_tools as bt
import lib
import wow

env = {}

with open("conf.json", "r") as conf_f:
    dct = json.load(conf_f)
env.update(dct)

bot = discord.Client()
DISCORD_BOT_TOKEN = env.get("token", "")
env["bot"] = bot

code = "сая"
vc = ""
vip = ['sndd_member', 'secret']
ddg = lib.DuckDuckGo()
crypto = lib.CryptoInfo(env.get('crypto_token', ''))


def check(message, check_word):
    return message.content.lower().startswith(code + check_word)


async def check_role(message):
    roles = bt.get_rolles(message)
    if not any(role in vip for role in roles):
        await bot.send_message(message.channel, 'Не я не могу это сделать по вашей просьбе...')
        raise Exception("[ERROR]: Not have permision for channel jump, %s" % message.author)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    q_module.reset()
    print('------')


def upd_voites(id, new_count):
    discript = helper.embed.description
    curent = discript.split(f"(start_id:{id})")[1].split(f'(end_id:{id})')[0]
    template = f"(start_id:{id}){curent}(end_id:{id})"
    new_template = f"(start_id:{id})[{new_count}](end_id:{id})"
    helper.embed.description = discript.replace(template, new_template)


def refresh_description(server=None):
    voiter_dct = q_module.get_question()
    for key in voiter_dct.keys():
        if key != "question":
            count = len(voiter_dct[key])
            upd_voites(key, count)


@bot.event
async def on_message(message, answered=False):
    player = bt.get_player(message.server)

    # if message.content.lower().startswith(code + "!"):
    #     finder(message)

    if message.content.lower().startswith("!_!"):
        print(message)
        print(message.channel)
        answered = True

    if message.content.lower().startswith("!!"):
        s_answer = str(message.content).split('!!')[1].strip()
        answer = int(s_answer)

        q_module.upd_question(answer, message)
        refresh_description()
        await bot.edit_message(helper.last_q, embed=helper.embed)
        answered = True

        # if "Direct Message" not in message.channel:
        #     q_module.upd_question(answer, message)
        #     refresh_description()
        #     await bot.edit_message(helper.last_q, embed=helper.embed)
        #     answered = True
        # else:
        #     serv_arg = re.findall(r'\[\[.*\]\]', message.content)
        #     if len(serv_arg) > 0:
        #         serv_arg = str(serv_arg[0])
        #         server = serv_arg[2:-2]
        #
        #         refresh_description(server)
        #         await bot.edit_message(helper.last_q, embed=helper.embed)
        #         answered = True

    if check(message, ' замути опрос'):
        question = str(message.content).split('замути опрос')[1].strip()
        variants = []
        server = None
        img = ""
        if "[[" in question:
            serv_arg = re.findall(r'\[\[.*\]\]', question)
            if len(serv_arg) > 0:
                serv_arg = str(serv_arg[0])
                server = serv_arg[2:-2]
            question = question.replace(serv_arg, "")

        if "((" in question:
            img_arg = re.findall(r'\(\(.*\)\)', question)
            if len(img_arg) > 0:
                img_arg = str(img_arg[0])
                img = img_arg[2:-2]
            question = question.replace(img_arg, "")

        if "--" in question:
            variants = question.split("--")[1:]
            question = question.split("--")[0]

        await q_module.crt_web_form(message, bot, question, variants, destanation=server, img=img)
        answered = True

    if check(message, ' сбрось опрос'):
        q_module.reset()
        answered = True

    if check(message, ' привет'):
        await bot.send_message(message.channel, '%s' % bt.hi_answer())
        answered = True

    if message.content.lower().startswith('все понятно?'):
        print('[command]: все понятно')
        await bot.send_message(message.channel, 'Всё понятно!')
        answered = True

    if check(message, ' который час?'):
        print('[command]: время')
        tm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        name = str(message.author).split("#")[0]
        await bot.send_message(message.channel, '%s господин %s!' % (tm, name))
        answered = True

    if check(message, ' прыгни в канал'):
        try:
            channel = str(message.content).split('канал')[1].strip()
            is_finded = False
            for ch in message.server.channels:
                if ch.name == channel:
                    # TODO change to => check_role(message) <-- need test
                    roles = bt.get_rolles(message)
                    if not any(role in vip for role in roles):
                        await bot.send_message(message.channel, 'Не я не могу это сделать по вашей просьбе...')
                        raise Exception("[ERROR]: Not have permision for channel jump, %s" % message.author)
                    vc = bot.voice_client_in(message.server)
                    if vc:
                        await vc.disconnect()
                    await bot.join_voice_channel(ch)
                    is_finded = True
                    await bot.send_message(message.channel, 'Туточки! ^_^')
                    break
            if not is_finded:
                await bot.send_message(message.channel, 'нет такого ТТ')
        except Exception as ex:
            print(ex)
            await bot.send_message(message.channel, 'что-то не пускает ТТ')
        answered = True

    if check(message, ' дай инфу по'):
        game = str(message.content).split("дай инфу по")[1]
        answer = bt.get_game_info(game)
        if answer:
            await bot.send_message(message.channel, '%s' % answer)
        else:
            await bot.send_message(message.channel, 'не знаю такой игры =\\')
        answered = True

    if 'кто в комнате?' in message.content:
        await bot.send_message(message.channel, 'Тут темно страшно и какой-то паладин лезет обниматься!')
        answered = True

    if check(message, ' кыкай каст'):
        await bot.send_message(message.channel, 'Сам кыкай %s бака!' % str(message.author).split("#")[0])
        answered = True

    if check(message, ' ты кто'):
        await bot.send_message(message.channel, 'Артефакт нейронной сети синедара,'
                                                ' и по совместительству скромный дворецкий сервера сндд')
        answered = True

    if check(message, ' что ты умеешь?'):
        await bot.send_message(message.channel, """
        Я умею петь песенки с youtube. Могу <тихо>, могу <громко>.
        Я могу подсказать время. <который час?>
        Могу патрулировать каналы этого сервера <прыгни в канал>
        Могу помочь с ссылками по играм. <дай инфу по>
        """)
        answered = True

    # ---------------------------------------- Плеер -----------------------------------------------------
    if check(message, ' отдать швартовы'):
        # ++++++++++++ Reset player
        if player:
            player.stop()
            player.replay = False
            sleep(3)
        else:
            player = bt.set_player(message.server, None)
        # ++++++++++++
        if bot.voice_client_in(message.server) is not None:
            await bot.voice_client_in(message.server).disconnect()

        voice_channel = message.author.voice_channel
        vc = await bot.join_voice_channel(voice_channel)
        url = "https://www.youtube.com/watch?v=yRh-dzrI4Z4"

        player.voice = vc
        if player.voice:
            player.player = await player.voice.create_ytdl_player(url)
            player.start()
            await bot.send_message(message.channel, 'Да капитан!')
        answered = True

    if check(message, ' спой'):
        await bt.start_song(message, bot)
        answered = True

    if check(message, ' замолкни'):
        await bot.send_message(message.channel, 'Ладно-ладно! Молчу!')
        player.stop()
        player.replay = False
        answered = True

    if check(message, ' повторяй '):
        url = bt.get_url(message.content.split("повторяй")[1])
        if player:
            player.stop()
            player.replay = False
            # TODO crush without sleep - fix later
            sleep(3)
        else:
            player = bt.set_player(message.server, None)
        player.voice = bot.voice_client_in(message.server)
        if player.voice:
            player.replay = True
            player.repeat(bot, url)
            await bot.send_message(message.channel, 'Так точно!')
        else:
            await bot.send_message(message.channel, 'Но я ведь не в канале ТТ')
        answered = True

    if check(message, ' слейся'):
        await bot.voice_client_in(message.server).disconnect()
        player.voice = None
        await bot.send_message(message.channel, 'Так точно! Только не ругаетесь! >_<')
        answered = True

    if check(message, ' тихо'):
        if player:
            await bot.send_message(message.channel, bt.q_answer())
            player.vol(0.1)
        else:
            await bot.send_message(message.channel, 'Так ведь это... Тишина же...')
        answered = True

    if check(message, ' громко'):
        if player:
            await bot.send_message(message.channel, bt.q_answer())
            player.vol(1.0)
        else:
            await bot.send_message(message.channel, 'Так ведь это... Тишина же...')
        answered = True

    if check(message, ' не шуми'):
        if player:
            await bot.send_message(message.channel, bt.q_answer())
            player.vol(0.5)
        else:
            await bot.send_message(message.channel, 'Так ведь это... Тишина же...')
        answered = True

    # if message.content.startswith(code + ' добавь в очередь '):
    #     # TODO queue
    #     await bot.send_message(message.channel, bt.you_answer())
    #     answered = True

    if check(message, ' установи громкость '):
        if player:
            value = str(message.content).split('установи громкость')[1].strip()
            await bot.send_message(message.channel, "Хорошо, устанавливаю громкость %s" % value)
            player.vol(float(value))
        else:
            await bot.send_message(message.channel, 'Так ведь это... Тишина же...')
        answered = True
    # ---------------------------------------- Плеер -----------------------------------------------------

    if check(message, 'wow'):
        await wow.answer(message, bot)
        answered = True

    if check(message, 'бака'):
        await bot.send_message(message.channel, 'Я бака!? Тебя давно в мокушку не кусали?! >_<')
        answered = True

    if check(message, ' ты '):
        await bot.send_message(message.channel, bt.you_answer())
        answered = True

    if check(message, ' запусти игру'):
        await bot.send_message(message.channel, 'Хорошо! Начинаем викторину!')
        try:
            screen = cinema_game.start_game(easy_mod=True)
            await bot.send_message(message.channel, screen)
        except:
            await bot.send_message(message.channel, 'Что-то не вышло... Давайте по новой')
        answered = True

    if message.content.lower().startswith("!это"):
        answer = str(message.content).split('!это')[1].strip()
        try:
            right_answer = cinema_game.game_try(answer)
            if right_answer:
                await bot.send_message(message.channel, "Ответ принят. Вы получаете 10 очков")
                await bot.send_message(message.channel, right_answer)
                screen = cinema_game.start_game(easy_mod=True)
                await bot.send_message(message.channel, "Продолжаем...")
                await bot.send_message(message.channel, screen)
            else:
                await bot.send_message(message.channel, "Неа!")
        except:
            await bot.send_message(message.channel, 'Что-то не вышло... Давайте по новой')
        answered = True

    if message.content.lower().startswith('!подсказка'):
        await bot.send_message(message.channel, 'Ладушки, посмотрим...')
        try:
            screen = cinema_game.next_screen()
            print("!подсказка", screen)
            if screen is not None:
                await bot.send_message(message.channel,'Даю подсказку, но учтите что выйгрыш становится меньше!')
                await bot.send_message(message.channel, screen)
            else:
                await bot.send_message('Увы, больше подсказок нету...')
        except:
            await bot.send_message(message.channel, 'Что-то не вышло... Давайте по новой')
        answered = True


    # try crypto rates
    if check(message, ""):
        text = message.content[len(code):]
        ans = await crypto.ask_if_possible(text)
        if ans is not None:
            if isinstance(ans, str):
                await bot.send_message(message.channel, ans)
            else:
                file = BytesIO(ans)
                await bot.send_file(message.channel, file, filename='chart.png')
            answered = True
    # check duck-duck-go query (see phrases in lib)
    if not answered and check(message, ""):
        text = message.content[len(code):]
        ans = await ddg.ask_if_possible(text)
        if ans is not None:
            # found something
            # TODO catch error: Attempt to decode JSON with unexpected mimetype: application/x-javascript
            print("debug ans: ", ans)
            if len(ans.strip()) > 0:
                await bot.send_message(message.channel, ans)
                answered = True

    if message.content.startswith(code + 'exit233'):
        sys.exit()

        # if message.content.startswith(bot + ' спой'):
        # vc.create_ytdl_player(url)

        # bot.add_comand(yt)

        # url = "https://youtu.be/YLb3Cpiqe-o"
        # author = message.author
        # voice_channel = author.voice_channel
        # vc = await client.join_voice_channel(voice_channel)
        #
        # player = await vc.create_ytdl_player(url)
        # player.volume = 0.1
        # player.start()

        # if message.content.startswith(bot + ' спой'):
        #     # url = str(message.content).split('канал')[1].strip()
        #     # bot.add_comand(yt)
        #     url = "https://youtu.be/YLb3Cpiqe-o"
        #     author = message.author
        #     voice_channel = author.voice_channel
        #     vc = await client.join_voice_channel(voice_channel)
        #
        #     player = await vc.create_ytdl_player(url)
        #     player.volume(0.2)
        #     player.stop()

    if check(message, " ") and not answered:
        await bot.send_message(message.channel, bt.random_answer())


# async def wrap(triger, answer):
#     if message.content.startswith(code + ' что ты умеешь?'):
#         await bot.send_message(message.channel, 'Тут темно страшно и какой-то паладин лезет обниматься!')
#         answered = True


bot.run(DISCORD_BOT_TOKEN)
