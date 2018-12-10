from datetime import datetime
import discord
import sys

import bot_tools as bt
import lib
import wow

bot = discord.Client()

DISCORD_BOT_TOKEN = ''

code = "сая"

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
    player = bt.get_player(message.server)

    if message.content.startswith(code + ' привет'):
        print('[command]: hi')
        await bot.send_message(message.channel, '%s' % bt.hi_answer())
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


    if message.content.startswith(code + ' дай инфу по'):
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

    if message.content.startswith(code + ' кыкай каст'):
        await bot.send_message(message.channel, 'Сам кыкай %s бака!' % str(message.author).split("#")[0])
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


    # ---------------------------------------- Плеер -----------------------------------------------------
    if message.content.startswith(code + ' спой'):
        await bt.start_song(message, bot)
        answered = True

    if message.content.startswith(code + ' замолкни'):
        await bot.send_message(message.channel, 'Ладно-ладно! Молчу!')
        player.stop()
        player.replay = False
        answered = True

    if message.content.startswith(code + ' повторяй '):
        url = bt.get_url(message.content.split("повторяй")[1])
        if player:
            player.stop()
            player.player=None
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

    if message.content.startswith(code + ' слейся'):
        await bot.voice_client_in(message.server).disconnect()
        player.voice = None
        await bot.send_message(message.channel, 'Так точно! Только не ругаетесь! >_<')
        answered = True

    if message.content.startswith(code + ' тихо'):
        if player:
            await bot.send_message(message.channel, bt.q_answer())
            player.vol(0.1)
        else:
            await bot.send_message(message.channel, 'Так ведь это... Тишина же...')
        answered = True

    if message.content.startswith(code + ' громко'):
        if player:
            await bot.send_message(message.channel, bt.q_answer())
            player.vol(1.0)
        else:
            await bot.send_message(message.channel, 'Так ведь это... Тишина же...')
        answered = True

    if message.content.startswith(code + ' не шуми'):
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

    if message.content.startswith(code + ' установи громкость '):
        if player:
            value = str(message.content).split('установи громкость')[1].strip()
            await bot.send_message(message.channel, "Хорошо, устанавливаю громкость %s" % value)
            player.vol(float(value))
        else:
            await bot.send_message(message.channel, 'Так ведь это... Тишина же...')
        answered = True
    # ---------------------------------------- Плеер -----------------------------------------------------

    if message.content.startswith(code + 'wow'):
        await wow.answer(message, bot)
        answered = True

    if message.content.startswith(code + 'бака'):
        await bot.send_message(message.channel, 'Я бака!? Тебя давно в мокушку не кусали?! >_<')
        answered = True

    if message.content.startswith(code + ' ты '):
        await bot.send_message(message.channel, bt.you_answer())
        answered = True
    # check duck-duck-go query (see phrases in lib)
    if message.content.startswith(code):
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

    if message.content.startswith(code + " ") and not answered:
        await bot.send_message(message.channel, bt.random_answer())


# async def wrap(triger, answer):
#     if message.content.startswith(code + ' что ты умеешь?'):
#         await bot.send_message(message.channel, 'Тут темно страшно и какой-то паладин лезет обниматься!')
#         answered = True


bot.run(DISCORD_BOT_TOKEN)
