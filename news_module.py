import datetime
import discord
import helper

async def news_form(chl, bot, theme, inform, img="https://pm1.narvii.com/6114/1a6566ee818390f7fcfdd80f14a88f64054a7cd2_hq.jpg",
                    ava="https://cdn.discordapp.com/app-icons/520189747013091348/c9dc0fb1eea59afa8fd0cdab5a7ade2c.png?size=64",
                    ):
    full_question = f" ```js\n {inform.strip()}```\n\n"

    ts = datetime.datetime.now().timestamp()
    embed = discord.Embed(title=theme,
                          colour=discord.Colour(0xf32bc9),
                          description=full_question,
                          timestamp=datetime.datetime.utcfromtimestamp(ts))

    embed.set_image(url=img)

    embed.set_thumbnail(
        url="https://cdn.pixabay.com/photo/2016/09/04/17/46/news-1644696_960_720.png")
    embed.set_author(name="МОДУЛЬ НОВОСТЕЙ",  # url="https://discordapp.com",
                     icon_url=ava)
    embed.set_footer(text="С вами была Сая. Рада стараться для вас!",
                     icon_url="")

    helper.last_q = await bot.send_message(chl, content="Доброго времени суток, я к вам с новостями.", embed=embed)
    helper.embed = embed