from datetime import datetime
import discord
import sys

import bot_tools
import lib
import wow

bot = discord.Client()

DISCORD_BOT_TOKEN = ''

code = "sndd"

vc = ""

ddg = lib.DuckDuckGo()


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_message(message, answered=False):
    if message.content.startswith(code + ' привет'):
        print('[command]: hi')
        await bot.send_message(message.channel, '%s' % bot_tools.hi_answer())
        answered = True

    if message.content.lower().startswith('все понятно?'):
        print('[command]: все понятно')
        await bot.send_message(message.channel, 'Всё понятно!')
        answered = True

    if message.content.startswith(code + ' который час?'):
        print('[command]: время')
        tm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        name = str(message.author).split("#")[0]
        await bot.send_message(message.channel, '%s господин %s!' % (tm, name))
        answered = True

    if message.content.startswith(code + ' прыгни в канал'):
        try:
            channel = str(message.content).split('канал')[1].strip()
            is_finded = False
            for ch in message.server.channels:
                if ch.name == channel:
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

    if message.content.startswith(code + ' спой'):
        await bot_tools.start_song(message, bot)
        answered = True

    if message.content.startswith(code + ' дай инфу по'):
        game = str(message.content).split("дай инфу по")[1]
        answer = bot_tools.get_game_info(game)
        if answer:
            await bot.send_message(message.channel, '%s' % answer)
        else:
            await bot.send_message(message.channel, 'не знаю такой игры =\\')
        answered = True

    if message.content.startswith(code + ' замолкни'):
        await bot.send_message(message.channel, 'Ладно-ладно! Молчу!')
        lib.player.stop()
        lib.player = None
        answered = True

    if message.content.startswith(code + ' тихо'):
        if lib.player:
            await bot.send_message(message.channel, bot_tools.q_answer())
            lib.player.volume = 0.1
        else:
            await bot.send_message(message.channel, 'Так ведь это... Тишина же...')
        answered = True

    if message.content.startswith(code + ' громко'):
        if lib.player:
            await bot.send_message(message.channel, bot_tools.q_answer())
            lib.player.volume = 1.0
        else:
            await bot.send_message(message.channel, 'Так ведь это... Тишина же...')
        answered = True

    if message.content.startswith(code + ' не шуми'):
        if lib.player:
            await bot.send_message(message.channel, bot_tools.q_answer())
            lib.player.volume = 0.5
        else:
            await bot.send_message(message.channel, 'Так ведь это... Тишина же...')
        answered = True

    if 'кто в комнате?' in message.content:
        await bot.send_message(message.channel, 'Тут темно страшно и какой-то паладин лезет обниматься!')
        lib.player.stop()
        answered = True

    if message.content.startswith(code + ' кыкай каст'):
        await bot.send_message(message.channel, 'Сам кыкай %s бака!' % str(message.author).split("#")[0])
        lib.player.stop()
        answered = True

    if message.content.startswith(code + ' ты кто'):
        await bot.send_message(message.channel, 'Артефакт нейронной сети синедара,'
                                                ' и по совместительству скромный дворецкий сервера сндд')
        answered = True

    if message.content.startswith(code + ' что ты умеешь?'):
        await bot.send_message(message.channel, """
        Я умею петь песенки с youtube. Могу <тихо>, могу <громко>.
        Я могу подсказать время. <который час?>
        Могу патрулировать каналы этого сервера <прыгни в канал>
        Могу помочь с ссылками по играм. <дай инфу по>
        """)
        answered = True

    if message.content.startswith(code + ' слейся'):
        voice_chat = bot.voice_client_in(message.server)
        await voice_chat.disconnect()
        await bot.send_message(message.channel, 'Так точно! Только не ругаетесь! >_<')
        answered = True

    if message.content.startswith(code + 'wow'):
        await wow.answer(message, bot)
        answered = True

    if message.content.startswith(code + 'бака'):
        await bot.send_message(message.channel, 'Я бака!? Тебя давно в мокушку не кусали?! >_<')
        answered = True

    if message.content.startswith(code + ' ты '):
        await bot.send_message(message.channel, bot_tools.you_answer())
        answered = True
    # check duck-duck-go query (see phrases in lib)
    if message.content.startswith(code):
        text = message.content[len(code):]
        ans = await ddg.ask_if_possible(text)
        if ans is not None:
            # found something
            await bot.send_message(message.channel, bot_tools.you_answer())
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

    if message.content.startswith(code + " ") and not answered:
        await bot.send_message(message.channel, bot_tools.random_answer())


# async def wrap(triger, answer):
#     if message.content.startswith(code + ' что ты умеешь?'):
#         await bot.send_message(message.channel, 'Тут темно страшно и какой-то паладин лезет обниматься!')
#         answered = True


bot.run(DISCORD_BOT_TOKEN)
