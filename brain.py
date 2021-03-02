import re
from datetime import datetime, time
from io import BytesIO
from time import sleep

import asyncio
from typing import List

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
import logging

from holidays import Calendar
from root import root, scheduler, Push, pushes
from bot_tools import env as env

# import modules to load them to knowledge
import general
import chrono
import integration

logging.basicConfig(level=logging.INFO)

integration.endpoints = env.get('integration', [])

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
        await message.channel.send( 'Не я не могу это сделать по вашей просьбе...')
        raise Exception("[ERROR]: Not have permision for channel jump, %s" % message.author)


async def fast_push():
    while True:
        try:
            response = await pushes('integration')  # type: List[Push]
            for push in response:
                channel = bot.get_channel(push.channel)
                await channel.send(channel, push.message)
        except Exception as ex:
            print(ex)
        await asyncio.sleep(1)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    q_module.reset()
    print('------')
    # asyncio.ensure_future(fast_push())
    # #start bg tasks
    # saved_dt = datetime.now().strftime('%Y-%m-%d')
    # saved_hour = -1
    # while True:
    #     try:
    #         now = datetime.now()
    #         tm = now.strftime('%Y-%m-%d %H:%M:%S')
    #         current_dt = now.strftime('%Y-%m-%d')
    #         print("start bg tasks", tm)
    #
    #         if now.hour != saved_hour:
    #             saved_hour = now.hour
    #             print('- new hour: %s' % str(saved_hour))
    #             # ================= New hour block
    #             # if env.get("ser_url", None) is not None:
    #             #
    #             #     url = env.get("ser_url", None)
    #             #     print("rq check ser" ,"%s/GetLastMonth" % url )
    #             #     res = requests.get("%s/GetLastMonth" % url)  # upd information from cbr
    #             #     print("Upd info:", res.text)
    #
    #             msg = None
    #             if now.hour == 9:
    #                 msg = await scheduler('morning')
    #                 # Dirty second use...
    #                 today = Calendar.today()
    #                 if today.type.is_working:
    #                     await bt.day_common_news(bot)
    #
    #             elif now.hour == 10:
    #                 await bt.check_today_price(bot, current_dt)
    #
    #             elif now.hour == 17:
    #                 msg = await scheduler('evening')
    #
    #             if msg is not None:
    #                 await bt.send_work_text(bot, msg)
    #
    #         print('- Is new day started? -', current_dt != saved_dt)
    #         if current_dt != saved_dt:
    #             # ================= New day block
    #             print('- new day -')
    #             saved_dt = current_dt
    #
    #     except Exception as ex:
    #         print(ex)
    #
    #     print('1 min')
    #     await asyncio.sleep(60)  # 1 minute


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
    player = bt.get_player(message.guild)

    if check(message, ' давай давай! лечиться!!!'):
        await bt.day_common_news(bot)
        # msg = await scheduler('evening')
        # await bt.send_work_test_text(bot, msg)
        answered = True

    if check(message, ' какие новости'):
        await bt.ask_common_news(bot, message)
        answered = True

    if check(message, ' лучший курс'):
        cur = str(message.content).split('лучший курс')[1].split('за')[0].strip()
        days = str(message.content).split('за')[1].split('дней')[0].strip()
        response, _ = bt.find_best_ser(cur, days)
        await message.channel.send("Легко!\n %s" % response)
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
        print(helper.last_q)
        # await bot.edit_message(helper.last_q, embed=helper.embed)
        await helper.last_q.edit(embed=helper.embed)
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
            await message.channel.send(answr)
            answered = True

    if check(message, ' сбрось опрос'):
        """info
            Могу сбросить опрос, команда: <сбрось опрос>
         info"""
        q_module.reset()
        answered = True

    # if check(message, ' !новость!'):
    #     block = str(message.content).split("!новость!")[1]
    #     theme = block.split("[[")[1].split("]]")[0]
    #     text = block.split("((")[1].split("))")[0]
    #     is_img = "@!@" in block and "@!@" in block
    #     if is_img:
    #         img = block.split("@!@")[1].split("@!@")[0]
    #         await bt.send_news(bot, theme, text, img)
    #     else:
    #         print("it")
    #         await bt.send_news(bot, theme, text)
    #     answered = True

    if message.content.lower().startswith('все понятно?'):
        print('[command]: все понятно')
        await message.channel.send( 'Всё понятно!')
        answered = True

    # if check(message, ' прыгни в канал'):
    #     """in-fo
    #         Могу скакать по каналам, команда: <прыгни в канал>
    #      info"""
    #     try:
    #         channel = str(message.content).split('канал')[1].strip()
    #         is_finded = False
    #         for ch in message.guild.channels:
    #             if ch.name == channel:
    #                 # TODO change to => check_role(message) <-- need test
    #                 # roles = bt.get_rolles(message)
    #                 # if not any(role in vip for role in roles):
    #                 #     await message.channel.send( 'Не я не могу это сделать по вашей просьбе...')
    #                 #     raise Exception("[ERROR]: Not have permision for channel jump, %s" % message.author)
    #                 vc = bot.voice_client_in(message.guild)
    #                 if vc:
    #                     await vc.disconnect()
    #                 await bot.join_voice_channel(ch)
    #                 is_finded = True
    #                 await message.channel.send( 'Туточки! ^_^')
    #                 break
    #         if not is_finded:
    #             await message.channel.send( 'нет такого ТТ')
    #     except Exception as ex:
    #         print(ex)
    #         await message.channel.send( 'что-то не пускает ТТ')
    #     answered = True

    if check(message, ' дай инфу по'):
        """info
            Могу дать информацию по некоторым играм, команда: <дай инфу по>
         info"""
        game = str(message.content).split("дай инфу по")[1]
        answer = bt.get_game_info(game)
        if answer:
            await message.channel.send( '%s' % answer)
        else:
            await message.channel.send( 'не знаю такой игры =\\')
        answered = True

    if check(message, ' посимь'):
        """info
            Могу симить персоажей на СД, команда: <посимь>
         info"""
        name = str(message.content).split("посимь")[1]
        try:
            await message.channel.send( 'Минутку.')
            answer = await bt.simc(name)
        except Exception as ex:
            print(ex)
            await message.channel.send( 'Что-то не удалось... Вы точно верно всё ввели?')
        if answer:
            await message.channel.send( '%s' % answer)
        else:
            await message.channel.send( 'не знаю такого =\\')
        answered = True

    # ---------------------------------------- Плеер -----------------------------------------------------
    if check(message, ' отдать швартовы'):
        # ++++++++++++ Reset player
        if player:
            player.stop()
            player.replay = False
            sleep(3)
        else:
            player = bt.set_player(message.guild, None)
        # ++++++++++++
        if bot.voice_client_in(message.guild) is not None:
            await bot.voice_client_in(message.guild).disconnect()

        voice_channel = message.author.voice_channel
        vc = await bot.join_voice_channel(voice_channel)
        url = "https://www.youtube.com/watch?v=yRh-dzrI4Z4"

        player.voice = vc
        if player.voice:
            player.player = await player.voice.create_ytdl_player(url)
            player.start()
            await message.channel.send( 'Да капитан!')
        answered = True

    # if check(message, ' спой'):
    #     """in-fo
    #         Могу спеть, команда: <спой> url_трека_на_youtube
    #      info"""
    #     await bt.start_song(message, bot)
    #     answered = True
    #
    # if check(message, ' замолкни'):
    #     """in-fo
    #         Могу перестать петь, команда: <замолкни>
    #      info"""
    #     await message.channel.send( 'Ладно-ладно! Молчу!')
    #     player.stop()
    #     player.replay = False
    #     answered = True
    #
    # if check(message, ' повторяй '):
    #     """in-fo
    #         Могу повторять песню, команда: <повторяй> url-трека-на-youtube
    #      info"""
    #     url = bt.get_url(message.content.split("повторяй")[1])
    #     if player:
    #         player.stop()
    #         player.replay = False
    #         # TODO crush without sleep - fix later
    #         sleep(3)
    #     else:
    #         player = bt.set_player(message.guild, None)
    #     player.voice = bot.voice_client_in(message.guild)
    #     if player.voice:
    #         player.replay = True
    #         player.repeat(bot, url)
    #         await message.channel.send( 'Так точно!')
    #     else:
    #         await message.channel.send( 'Но я ведь не в канале ТТ')
    #     answered = True
    #
    # if check(message, ' слейся'):
    #     """in-fo
    #         Могу покинуть канал, команда: <слейся>
    #      info"""
    #     await bot.voice_client_in(message.guild).disconnect()
    #     player.voice = None
    #     await message.channel.send( 'Так точно! Только не ругаетесь! >_<')
    #     answered = True
    #
    # if check(message, ' тихо'):
    #     """in-fo
    #        Могу петь тихо, команда: <тихо>
    #     info"""
    #     if player:
    #         await message.channel.send( bt.q_answer())
    #         player.vol(0.1)
    #     else:
    #         await message.channel.send( 'Так ведь это... Тишина же...')
    #     answered = True
    #
    # if check(message, ' громко'):
    #     """in-fo
    #        Могу петь громко, команда: <громко>
    #     info"""
    #     if player:
    #         await message.channel.send( bt.q_answer())
    #         player.vol(1.0)
    #     else:
    #         await message.channel.send( 'Так ведь это... Тишина же...')
    #     answered = True
    #
    # if check(message, ' не шуми'):
    #     """in-fo
    #        Могу установить среднюю громкость, команда: <не шуми>
    #     info"""
    #     if player:
    #         await message.channel.send( bt.q_answer())
    #         player.vol(0.5)
    #     else:
    #         await message.channel.send( 'Так ведь это... Тишина же...')
    #     answered = True
    #
    # if check(message, ' установи громкость '):
    #     """in-fo
    #         Могу установить громкость по вашему желанию, команда: <установи громкость> 0.09
    #     info"""
    #     if player:
    #         value = str(message.content).split('установи громкость')[1].strip()
    #         await message.channel.send( "Хорошо, устанавливаю громкость %s" % value)
    #         player.vol(float(value))
    #     else:
    #         await message.channel.send( 'Так ведь это... Тишина же...')
    #     answered = True
    # ---------------------------------------- Плеер -----------------------------------------------------

    if check(message, 'wow'):
        await wow.answer(message, bot)
        answered = True

    if check(message, ' запусти викторину'):
        """info
            Могу устраивать кино викторины, команда: <запусти викторину>
        info"""
        await message.channel.send( 'Хорошо! Начинаем викторину!')
        try:
            screen = cinema_game.start_game(message.guild, easy_mod=True)
            await message.channel.send( screen)
            await message.channel.send(
                                   "Для ответа напишите '!это название_фильма' для подсказки введите '!подсказка'")
        except Exception as ex:
            bt.log(ex)
            await message.channel.send( 'Что-то не вышло... Давайте по новой')
        answered = True

    if message.content.lower().startswith("!это"):
        answer = str(message.content).split('!это')[1].strip()
        try:
            right_answer = cinema_game.game_try(answer, message.guild)
            if right_answer:
                points = cinema_game.get_points()
                current_points = cinema_game.add_points_to_user(str(message.author))
                await message.channel.send(
                                       f"Ответ принят. " + str(right_answer) + f" Вы получаете {points} очков.")
                await message.channel.send( "Рейтинг игроков: " + str(current_points) + " Продолжаем...")
                screen = cinema_game.start_game(message.guild, easy_mod=True)
                await message.channel.send( screen)
            else:
                await message.channel.send( "Неа!")
        except Exception as ex:
            bt.log(ex)
            await message.channel.send( 'Что-то не вышло... Давайте по новой')
        answered = True

    if message.content.lower().startswith('!подсказка'):
        await message.channel.send( 'Ладушки, посмотрим...')
        try:
            tip = cinema_game.get_tip(message.guild)
            print("!подсказка", tip)
            if tip is not None:
                await message.channel.send( 'Даю подсказку, но учтите что выйгрыш становится меньше!')
                await message.channel.send( tip)
            else:
                await message.channel.send('Увы, больше подсказок нету...')
        except Exception as ex:
            bt.log(ex)
            await message.channel.send( 'Что-то не вышло... Давайте по новой')
        answered = True

    # try crypto rates
    # if check(message, ""):
    #     """in-fo
    #         Могу подсказать динамику криптовалюты, команда: <динамика>/<какой курс> валюта
    #     info"""
    #     text = message.content[len(code):]
    #     ans = await crypto.ask_if_possible(text)
    #     if ans is not None:
    #         if isinstance(ans, str):
    #             await message.channel.send( ans)
    #         else:
    #             file = BytesIO(ans)
    #             await bot.send_file(message.channel, file, filename='chart.png')
    #         answered = True
    # calc
    if not answered and check(message, ""):
        """info
            Могу считать, команда: <посчитай> 2+2
        info"""
        text = message.content[len(code):]
        ans = await calc.ask_if_possible(text)
        if ans is not None:
            await message.channel.send(ans)
            answered = True

    reply = await root(message.content, raw_message=message, bot=bot)
    if reply is not None:
        if isinstance(reply, str):            
            await message.channel.send(reply)
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
                await message.channel.send( ans)
                answered = True

    if message.content.startswith(code + 'exit233'):
        sys.exit()

    if check(message, " ") and not answered:
        await message.channel.send( bt.random_answer())


bot.run(DISCORD_BOT_TOKEN)
# bot.run("")
