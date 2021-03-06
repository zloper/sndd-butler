"""
time related knowledge
"""
import random
import time

from holidays import Calendar, DayType
from root import root, scheduler

__stay_alive = [
    'выдержить',
    'продержаться',
    'сдюжить',
]


@root.regexp(r'добр(ого|ое|ый)[ ]+(дня|день|времени|утро|утра|утречка)')
async def brief(message: str, **kwargs):
    text = 'Доброго дня!'
    today = Calendar.today()
    left = Calendar.left_working_days()

    prev = Calendar.non_working_days_before()
    if len(prev) > 2:
        text += f'\nНадеюсь {len(prev)} дня вы провели итересно и классно отдохнули'
    elif len(prev) == 2:
        text += '\nЭти выходные, я надеюсь, у вас были хорошие'
    elif len(prev) > 0:
        text += '\nУспели отдохнуть за выходной?'

    text += f'\nСегодня {today.stamp.strftime("%d.%m.%Y")}'
    if not today.type.is_working:
        text += ' и это выходной!'
    elif today.type == DayType.SHORT:
        text += ' и это корокий день ;-)'
    else:
        alive = random.choice(__stay_alive)
        left_txt = 'денёк' if len(left) == 2 else f'{len(left) - 1} дня'
        text += f' и осталось {alive} еще {left_txt} перед выходными, не считая сегодня'

    tomorrow = Calendar.tomorrow()

    if not tomorrow.type.is_working:
        text += '\nА завтра' + (' ' if today.type.is_working else ' тоже ') + 'выходной, кстати!'
        if tomorrow.holiday is not None:
            text += ' ' + tomorrow.holiday.title
    elif not today.type.is_working and tomorrow.type.is_working:
        text += '\nЗавтра на работу =('
    if not today.type.is_working and len(prev) > 0 and not tomorrow.type.is_working:
        text += '\n\nЯ тут подумала: а что вы тут вообще делаете посреди выходных? o_0'
    return text


@scheduler.simple('morning')
async def auto_brief(message: str, **kwargs):
    today = Calendar.today()
    if today.type.is_working:
        result = await brief(message)
        result += '\nВсем добра!\nhttps://cataas.com/cat/cute?q=' + str(time.time())
        return result


@scheduler.simple('evening')
async def auto_goodbay(message: str, **kwargs):
    today = Calendar.today()
    if today.type.is_working:
        result = await goodbay(message)
        return result


async def goodbay(message: str, **kwargs):
    today = Calendar.today()
    if today.type.is_working:
        return "Доброго вечера господа!\n Рабочий день медленно но верно приближается к концу. \n" \
           "Я только хотела напомнить вам - пожалуйста не перетруждайтесь.\n И спасибо вам за труд."
