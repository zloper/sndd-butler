import os
from enum import Enum
from typing import NamedTuple, Dict, List, Optional
from datetime import datetime, timedelta

import requests
from xml.etree import ElementTree as ET


class Holiday(NamedTuple):
    id: str
    title: str


class DayType(Enum):
    HOLIDAY = 1
    SHORT = 2
    WORKING_WEEKEND = 3
    WORKDAY = 4
    WEEKEND = 5

    @property
    def is_working(self) -> bool:
        return self in (DayType.WORKDAY, DayType.WORKING_WEEKEND, DayType.SHORT)


class Day(NamedTuple):
    type: DayType
    month: int
    day: int
    holiday_id: Optional[str] = None


class Info(NamedTuple):
    type: DayType
    stamp: datetime
    holiday: Optional[Holiday] = None


class Calendar:
    _years = {}  # type: Dict[int, Calendar]

    def __init__(self, all_holidays: List[Holiday], all_days: List[Day]):
        self.holidays = {}  # type: Dict[str, Holiday]
        self.days = all_days  # type: List[Day]
        for h in all_holidays:
            self.holidays[h.id] = h

    @classmethod
    def today(cls) -> Info:
        """
        Get today info
        """
        return cls.day(datetime.now())

    @classmethod
    def tomorrow(cls) -> Info:
        """
        Get next day info
        """
        return cls.day(datetime.now() + timedelta(days=1))

    @classmethod
    def non_working_days_before(cls, at: datetime = None) -> List[Info]:
        """
        Get all non working days before specified time
        :param at: specific timestamp or now if None
        """
        if at is None:
            at = datetime.now() - timedelta(days=1)
        ans = []
        while True:
            info = cls.day(at)
            if not info.type.is_working:
                ans.append(info)
                at = at - timedelta(days=1)
            else:
                break
        return ans

    @classmethod
    def left_working_days(cls, at: datetime = None) -> List[Info]:
        """
        Get all working days (including current) till next non-working days
        :param at: specific timestamp or now if None
        """
        if at is None:
            at = datetime.now()
        ans = []
        while True:
            info = cls.day(at)
            if info.type.is_working:
                ans.append(info)
                at = at + timedelta(days=1)
            else:
                break
        return ans

    @classmethod
    def day(cls, at: datetime) -> Info:
        """
        Get day info at specific time
        """
        calendar = cls.get(at.year)
        for day in calendar.days:
            if day.month == at.month and day.day == at.day:
                return Info(
                    type=day.type,
                    stamp=at,
                    holiday=calendar.holidays.get(day.holiday_id),
                )
        weekend = 5 <= at.weekday() <= 6
        day_type = DayType.WEEKEND if weekend else DayType.WORKDAY
        if at.weekday() == 4:
            day_type = DayType.SHORT
        return Info(
            type=day_type,
            stamp=at,
        )

    @classmethod
    def get(cls, year: int = None, cache_dir: str = './cache/calendar') -> 'Calendar':
        """
        Get calendar for year from cache or URL
        :param year: interesting year. if none - current year means
        :param cache_dir: directory of cache
        :return: instance of working calendar
        """
        if year is None:
            year = datetime.now().year
        calendar = cls._years.get(year)
        if calendar is None:
            calendar = cls.__fetch(year, cache_dir)
            cls._years[year] = calendar
        return calendar

    @classmethod
    def __fetch(cls, year: int, cache_dir: str) -> 'Calendar':
        file = os.path.join(cache_dir, str(year) + '.xml')
        try:
            with open(file, 'rt') as f:
                content = f.read()
        except FileNotFoundError:
            r = requests.get(f'http://xmlcalendar.ru/data/ru/{year}/calendar.xml')
            r.encoding = 'utf8'
            content = r.text
        calendar = cls.__parse(content)
        try:
            os.makedirs(cache_dir, exist_ok=True)
            with open(file, 'wt') as f:
                f.write(content)
        except IOError:
            pass
        return calendar

    @staticmethod
    def __parse(content: str) -> 'Calendar':
        document = ET.fromstring(content)  # type: ET.ElementTree
        days = []
        holidays = []
        for holiday in document.iterfind('holidays/holiday'):
            holidays.append(Holiday(
                id=holiday.attrib['id'],
                title=holiday.attrib['title'],
            ))

        for day in document.iterfind('days/day'):
            m, d = day.attrib['d'].split('.')
            days.append(Day(
                type=DayType(int(day.attrib['t'])),
                day=int(d),
                month=int(m),
                holiday_id=day.attrib.get('h'),
            ))

        return Calendar(holidays, days)
