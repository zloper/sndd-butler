import re
from datetime import datetime, time
from io import BytesIO
from time import sleep

import asyncio

import requests

import cinema_game
import helper
import mus_module
import q_module
import discord
import sys
import bot_tools as bt
import lib
import wow
from root import root, scheduler
from bot_tools import env as env

# import modules to load them to knowledge
import general
import chrono

bot = discord.Client()
DISCORD_BOT_TOKEN = env.get("token", "")
env["bot"] = bot

code = "сая"
vc = ""
vip = ['sndd_member', 'secret']
ddg = lib.DuckDuckGo()
crypto = lib.CryptoInfo(env.get('crypto_token', ''))
calc = lib.Calculator()


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

    # start bg tasks
    saved_dt = datetime.now().strftime('%Y-%m-%d')
    saved_hour = -1
    while True:

        now = datetime.now()
        tm = now.strftime('%Y-%m-%d %H:%M:%S')
        current_dt = now.strftime('%Y-%m-%d')
        print("start bg tasks", tm)

        if now.hour != saved_hour:
            saved_hour = now.hour
            print('- new hour: %s' % str(saved_hour), current_dt != saved_dt)
            # ================= New hour block
            if env.get("ser_url", None) is not None:
                url = env.get("ser_url", None)
                res = requests.get("%s/GetLastMonth" % url)  # upd information from cbr
                print("Upd info:", res.text)

            msg = None
            if now.hour == 9:
                msg = await scheduler('morning')
            elif now.hour == 17:
                msg = await scheduler('evening')

            if msg is not None:
                await bt.send_work_text(bot, msg)

        print('- Is new day started? -', current_dt != saved_dt)
        if current_dt != saved_dt:
            # ================= New day block
            saved_dt = current_dt
            await bt.check_today_price(bot, current_dt)
        await asyncio.sleep(60*10)  # 10 minute


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

    if check(message, ' давай давай лечиться!'):
        # await bt.check_today_price(bot, "2019-05-07")
        msg = await scheduler('evening')
        await bt.send_work_test_text(bot, msg)
        answered = True

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

    if check(message, ' замути опрос'):
        """info
           Умею создавать опросы, команда: <замути опрос> текст-вопроса --ответ1 --ответ2 ((url-кратинки-для-опроса))
        info"""
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

    if check(message, '!'):
        """info
          Могу выдать аниме coub: <сая! давай аниме> и если приглянулась мелодия могу дать ссылку на трек <сая! скинь трек>
       info"""
        answr = mus_module.finder(message)
        if answr is not None:
            await bot.send_message(message.channel, answr)
            answered = True

    if check(message, ' сбрось опрос'):
        """info
            Могу сбросить опрос, команда: <сбрось опрос>
         info"""
        q_module.reset()
        answered = True

    if check(message, ' !новость!'):
        block = str(message.content).split("!новость!")[1]
        theme = block.split("[[")[1].split("]]")[0]
        text = block.split("((")[1].split("))")[0]
        is_img = "@!@" in block and "@!@" in block
        if is_img:
            img = block.split("@!@")[1].split("@!@")[0]
            await bt.send_news(bot, theme, text, img)
        else:
            print("it")
            await bt.send_news(bot, theme, text)
        answered = True

    if message.content.lower().startswith('все понятно?'):
        print('[command]: все понятно')
        await bot.send_message(message.channel, 'Всё понятно!')
        answered = True

    if check(message, ' прыгни в канал'):
        """info
            Могу скакать по каналам, команда: <прыгни в канал>
         info"""
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
        """info
            Могу дать информацию по некоторым играм, команда: <дай инфу по>
         info"""
        game = str(message.content).split("дай инфу по")[1]
        answer = bt.get_game_info(game)
        if answer:
            await bot.send_message(message.channel, '%s' % answer)
        else:
            await bot.send_message(message.channel, 'не знаю такой игры =\\')
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
        """info
            Могу спеть, команда: <спой> url_трека_на_youtube
         info"""
        await bt.start_song(message, bot)
        answered = True

    if check(message, ' замолкни'):
        """info
            Могу перестать петь, команда: <замолкни>
         info"""
        await bot.send_message(message.channel, 'Ладно-ладно! Молчу!')
        player.stop()
        player.replay = False
        answered = True

    if check(message, ' повторяй '):
        """info
            Могу повторять песню, команда: <повторяй> url-трека-на-youtube
         info"""
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
        """info
            Могу покинуть канал, команда: <слейся>
         info"""
        await bot.voice_client_in(message.server).disconnect()
        player.voice = None
        await bot.send_message(message.channel, 'Так точно! Только не ругаетесь! >_<')
        answered = True

    if check(message, ' тихо'):
        """info
           Могу петь тихо, команда: <тихо>
        info"""
        if player:
            await bot.send_message(message.channel, bt.q_answer())
            player.vol(0.1)
        else:
            await bot.send_message(message.channel, 'Так ведь это... Тишина же...')
        answered = True

    if check(message, ' громко'):
        """info
           Могу петь громко, команда: <громко>
        info"""
        if player:
            await bot.send_message(message.channel, bt.q_answer())
            player.vol(1.0)
        else:
            await bot.send_message(message.channel, 'Так ведь это... Тишина же...')
        answered = True

    if check(message, ' не шуми'):
        """info
           Могу установить среднюю громкость, команда: <не шуми>
        info"""
        if player:
            await bot.send_message(message.channel, bt.q_answer())
            player.vol(0.5)
        else:
            await bot.send_message(message.channel, 'Так ведь это... Тишина же...')
        answered = True

    if check(message, ' установи громкость '):
        """info
            Могу установить громкость по вашему желанию, команда: <установи громкость> 0.09
        info"""
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

    if check(message, ' запусти игру'):
        """info
            Могу устраивать викторины, команда: <запусти игру>
        info"""
        await bot.send_message(message.channel, 'Хорошо! Начинаем викторину!')
        try:
            screen = cinema_game.start_game(message.server, easy_mod=True)
            await bot.send_message(message.channel, screen)
            await bot.send_message(message.channel,
                                   "Для ответа напишите '!это название_фильма' для подсказки введите '!подсказка'")
        except Exception as ex:
            bt.log(ex)
            await bot.send_message(message.channel, 'Что-то не вышло... Давайте по новой')
        answered = True

    if message.content.lower().startswith("!это"):
        answer = str(message.content).split('!это')[1].strip()
        try:
            right_answer = cinema_game.game_try(answer, message.server)
            if right_answer:
                points = cinema_game.get_points()
                current_points = cinema_game.add_points_to_user(str(message.author))
                await bot.send_message(message.channel,
                                       f"Ответ принят. " + str(right_answer) + f" Вы получаете {points} очков.")
                await bot.send_message(message.channel, "Рейтинг игроков: " + str(current_points) + " Продолжаем...")
                screen = cinema_game.start_game(message.server, easy_mod=True)
                await bot.send_message(message.channel, screen)
            else:
                await bot.send_message(message.channel, "Неа!")
        except Exception as ex:
            bt.log(ex)
            await bot.send_message(message.channel, 'Что-то не вышло... Давайте по новой')
        answered = True

    if message.content.lower().startswith('!подсказка'):
        await bot.send_message(message.channel, 'Ладушки, посмотрим...')
        try:
            tip = cinema_game.get_tip(message.server)
            print("!подсказка", tip)
            if tip is not None:
                await bot.send_message(message.channel, 'Даю подсказку, но учтите что выйгрыш становится меньше!')
                await bot.send_message(message.channel, tip)
            else:
                await bot.send_message('Увы, больше подсказок нету...')
        except Exception as ex:
            bt.log(ex)
            await bot.send_message(message.channel, 'Что-то не вышло... Давайте по новой')
        answered = True

    # try crypto rates
    if check(message, ""):
        """info
            Могу подсказать динамику криптовалюты, команда: <динамика>/<какой курс> валюта
        info"""
        text = message.content[len(code):]
        ans = await crypto.ask_if_possible(text)
        if ans is not None:
            if isinstance(ans, str):
                await bot.send_message(message.channel, ans)
            else:
                file = BytesIO(ans)
                await bot.send_file(message.channel, file, filename='chart.png')
            answered = True
    # calc
    if not answered and check(message, ""):
        """info
            Могу считать, команда: <посчитай> 2+2
        info"""
        text = message.content[len(code):]
        ans = await calc.ask_if_possible(text)
        if ans is not None:
            await bot.send_message(message.channel, ans)
            answered = True

    reply = await root(message.content, raw_message=message, bot=bot)
    if reply is not None:
        if isinstance(reply, str):
            await bot.send_message(message.channel, reply)
        else:
            file = BytesIO(reply)
            await bot.send_file(message.channel, file, filename='chart.png')
        answered = True

    # check duck-duck-go query (see phrases in lib)
    if not answered and check(message, ""):
        """info
            Могу подсказывать определения, команда: <что такое> вопрос
        info"""
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

    if check(message, " ") and not answered:
        await bot.send_message(message.channel, bt.random_answer())


bot.run(DISCORD_BOT_TOKEN)
