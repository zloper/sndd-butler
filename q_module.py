import datetime
import discord
import yaml

import helper


def parse_server(destanation, bot, msg):
    srv = destanation.split("/")[0]
    ch = destanation.split("/")[1]
    for server in bot.servers:
        if str(server).lower() == srv.strip().lower():
            for channel in server.channels:
                if str(channel) == "Голосовые каналы":
                    break
                if str(channel).lower() == ch.strip().lower():
                    return channel
    return msg.channel


async def crt_web_form(message, bot, question, answers=[], img="",
                       ava="https://lh4.googleusercontent.com/d2p5iwxQTtEIKAg0fdOz0ZfgXdcM_8VYAJq7yLK_vkUlVioPxXNbRPCdUNfKz_0rEamkVWlm-dq7Sw=w1920-h886",
                       destanation=None):
    full_question = f" ```python\n '{question.strip()}'```\n\n"
    i = 0
    for answer in answers:
        i += 1
        string = f"```css\n [!!{i}] - {answer}```[Голосов ](start_id:{i})[0](end_id:{i})\n\n"
        full_question += string

    if destanation is None:
        destanation = message.channel
    else:
        destanation = parse_server(destanation, bot, message)

    embed = discord.Embed(title="Опрос:",
                          colour=discord.Colour(0xf32bc9),
                          description=full_question,
                          timestamp=datetime.datetime.utcfromtimestamp(1545113261))

    embed.set_image(url=img)

    embed.set_thumbnail(
        url=ava)
    embed.set_author(name="Вопрос от саечки!",  # url="https://discordapp.com",
                     icon_url=ava)
    embed.set_footer(text="ждем ваших ответов",
                     icon_url=ava)

    storage = {'question': question.strip()}
    for i in range(len(answers)):
        id = i + 1
        storage[id] = []
    save_question(storage)

    helper.last_q = await bot.send_message(destanation, content="время опроса!", embed=embed)
    helper.embed = embed


def save_question(dct):
    with open("question.yaml", "w") as f:
        f.write(str(dct))


def get_question():
    with open("question.yaml", "r") as f:
        res = f.read()
        j_res = yaml.load(res)
    return j_res


def upd_question(answer_id, message):
    answer_id = int(answer_id)
    question = get_question()
    if question == {}:
        print("Нет текущего опроса")
        return

    if answer_id in question.keys():
        # ---- remove old answer ------
        author = str(message.author)
        for num in question.keys():
            voiters = question[num]
            if author in voiters:
                voiters.remove(author)
                question[num] = voiters

        # ------ add new answer ---------
        question[answer_id].append(author)
        save_question(question)
        return question.get("msg", None)
        # -------------------------------
    else:
        print("Нет такого варианта")


def reset():
    save_question({})
