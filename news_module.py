import datetime
import discord
import helper

async def news_form(chl, bot, theme, inform, img="",
                    ava="https://cdn.discordapp.com/app-icons/520189747013091348/c9dc0fb1eea59afa8fd0cdab5a7ade2c.png?size=64",
                    ):
    full_question = f" ```js\n {inform.strip()}```\n\n"

    embed = discord.Embed(title=theme,
                          colour=discord.Colour(0xf32bc9),
                          description=full_question,
                          timestamp=datetime.datetime.utcfromtimestamp(1545113261))

    embed.set_image(url=img)

    embed.set_thumbnail(
        url="https://ittechnews.net/wp-content/uploads/2018/03/News-Button.jpg")
    embed.set_author(name="МОДУЛЬ НОВОСТЕЙ",  # url="https://discordapp.com",
                     icon_url=ava)
    embed.set_footer(text="С вами была Сая. Рада стараться для вас!",
                     icon_url="")

    helper.last_q = await bot.send_message(chl, content="Доброго времени суток, я к вам с новостями.", embed=embed)
    helper.embed = embed