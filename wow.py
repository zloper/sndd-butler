async def answer(message, bot):
    msg = message.content.split("snddwow")[1].strip()

    args = msg.split(" ")
    url = "https://www.warcraftlogs.com/zone/rankings/"
    boss = args[1].lower().strip()
    end_url=adress_book(boss)
    if end_url:
        final_url = url + adress_book(boss)
        await bot.send_message(message.channel, 'Да господин, вот ваша ссылка  ^_^: %s' % final_url)
    else:
        await bot.send_message(message.channel, 'Не знаю такого >_<')


def adress_book(boss):
    end_url = None

    if boss == "vectis" or boss == "вектис":
        end_url = "19#boss=2134"

    if boss == "taloc" or boss == "талок":
        end_url = "19#boss=2144"

    if boss == "mother" or boss == "мамка":
        end_url = "19#boss=2141"

    if boss == "fetid" or boss == "собака":
        end_url = "19#boss=2128"

    if boss == "zekvoz" or boss == "завхоз":
        end_url = "19#boss=2136"

    if boss == "zul" or boss == "зул":
        end_url = "19#boss=2145"

    if boss == "mytrax" or boss == "митракс":
        end_url = "19#boss=2135"

    if boss == "guun" or boss == "гун":
        end_url = "19#boss=2122"

    return end_url
