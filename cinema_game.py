import os
import random

import requests
import re

import yaml

import imdb

base = "https://www.imdb.com/"


# TODO TIPS
# TODO another titles

def refs_to_list(raw_txt):
    raw_links = re.findall(r'<a href="/title/t.*\"', raw_txt)
    links_list = []
    for href in raw_links:
        work_link = str(href.split('<a href=')[1])
        work_link = work_link.replace('"', '')
        work_link = base + str(work_link)[1:]
        if " " in work_link:
            work_link = work_link.split(" ")[0]
        links_list.append(work_link)
    result = list(set(links_list))
    return result


def get_random_movie(start_year="2010", min_rate="7.0", mv_type="action", easy_mod=False):
    pages = ["", "start=251&ref_=adv_nxt", "&start=501&ref_=adv_nxt", "&start=751&ref_=adv_nxt",
             "&start=1001&ref_=adv_nxt",
             "&start=1251&ref_=adv_nxt", "&start=1501&ref_=adv_nxt", "&start=1751&ref_=adv_nxt",
             "&start=2001&ref_=adv_nxt"]
    r_page = random.choice(pages)
    url = f"{base}search/title?release_date={start_year}-01-01,2018-12-31&user_rating={min_rate},10.0&num_votes=500,&genres={mv_type}&view=simple&count=250{r_page}"

    if easy_mod:
        companies = ['fox', 'sony', 'dreamworks', 'paramount', 'universal', 'disney', 'warner']
        company = random.choice(companies)

        url = f"{base}search/title?release_date={start_year}-01-01,2018-12-31&user_rating=,10.0&num_votes=100,&companies={company}&view=simple&count=250"

    r = requests.get(url)
    txt = r.text

    movie_list = refs_to_list(txt)

    result = random.choice(movie_list)
    return result


def parse_film(url):
    mv_info = {}
    mv_info["url"] = url
    r = requests.get(url)
    txt = r.text
    mv_obj = imdb.parse_movie(txt)
    title = txt.split('<div class="title_wrapper">')[1]
    title = title.split('</h1>')[0]
    title = title.split("&nbsp")[0].split(">")[1]
    title = title.lower().strip()
    orig_title = ""
    parent_title = ""
    if 'class="originalTitle"' in txt:
        orig_title = txt.split('<div class="originalTitle">')[1].split('<span class="description">')[0]
        orig_title = orig_title.lower().strip()
    if '<div class="titleParent">' in txt:
        parent_title = txt.split('<div class="titleParent">')[1].split('title="')[1].split('"')[0]
        parent_title = parent_title.lower().strip()

    titles = [title, orig_title, parent_title, mv_obj.title]
    mv_info["title"] = list(filter(None, titles))
    mv_info["description"] = mv_obj.description.replace("/", " - ").replace("\\", " - ")
    mv_info["poster"] = mv_obj.poster_url
    mv_info["genre"] = mv_obj.genre
    mv_info['actors'] = mv_obj.actors
    # mv_info['review'] = mv_obj.review

    ender = url.split("/")[-1]
    screens_url = url.replace(ender, "mediaindex?ref_=tt_pv_mi_sm")

    mv_info["screens_url"] = screens_url

    r = requests.get(screens_url)
    s_txt = r.text

    start_block = 'id="media_index_content"'
    end_block = 'class="article listo"'
    raw_screens = s_txt.split(start_block)[1].split(end_block)[0]

    screens_list = refs_to_list(raw_screens)

    mv_info['screens'] = screens_list
    return mv_info


def save_mv(dct):
    with open("movie_game.yaml", "w") as f:
        f.write(str(dct))


def get_mv():
    with open("movie_game.yaml", "r") as f:
        res = f.read()
        j_res = yaml.load(res)
    return j_res


def open_screen(url):
    r = requests.get(url)
    txt = r.text
    screens = re.findall(r'"https://m.media-amazon.com/images/.*\.jpg"', txt)
    return screens[0]


def get_and_rm_screen(movie):
    scr_list = movie['screens']
    if len(scr_list) > 0:
        if len(scr_list) == 1:
            scr = scr_list.pop()
            movie['screens'] = scr_list
            save_mv(movie)
            return scr
        nums = range(1, len(scr_list))
        rand = random.choice(nums)

        scr = scr_list.pop(rand)
        movie['screens'] = scr_list
        save_mv(movie)
        return scr
    else:
        print("SCREENS ENDED!")


def start_game(easy_mod=False):
    set_points(35)
    mv = get_random_movie(easy_mod=easy_mod)
    movie = parse_film(mv)
    scrn = get_and_rm_screen(movie)
    res = open_screen(scrn)
    return res


def next_screen(movie):
    scrn = get_and_rm_screen(movie)
    print(scrn)
    if scrn is not None:
        res = open_screen(scrn)
        print(res)
        return res
    else:
        print("Not have screens for hints =(")
        return None


def game_try(answer):
    movie = get_mv()
    if movie == {}:
        print("game not exist")
        return False

    win_words = movie['title']
    answer = answer.lower().strip()
    if answer == "":
        print("empty answer")
        return False

    if answer in win_words:
        print("YES!")
        save_mv({})
        return win_words

    # hardcore check
    if ' ' in answer:
        answer = answer.split(' ')
        for title in win_words:
            check_title = title
            hit = 0
            for answ in answer:
                if answ in check_title:
                    check_title = check_title.replace(answ, '')
                    hit += 1
            if hit >= len(answer) - 1:
                print("some yes...")
                save_mv({})
                return win_words

    print("NO")
    return False


def next_text(movie):
    text = movie['description']
    for title in movie['title']:
        text = text.lower().replace(title, "**********")
    if "." in text:
        text_list = text.split(".")
        text_list = list(filter(None, text_list))
        res = text_list.pop(0)
        movie['description'] = text.replace(res, "")
        save_mv(movie)
        return res
    else:
        movie['description'] = ""
        save_mv(movie)
        return text


def get_points():
    with open("game_bank", 'a') as f:
        f.write('')
    with open("game_bank", 'r') as f:
        res = (f.read())

    if res.strip() == "":
        res = 35
    else:
        res = int(res)
    return res


def set_points(points):
    with open("game_bank", 'w') as f:
        f.write(str(points))


def get_tip():
    points = get_points()
    movie = get_mv()
    if movie == {}:
        print("game not exist")
        return

    tips_list = ["screen"]
    if movie.get('genre', "None") != "None":
        tips_list.append("genre")
    if movie.get('actors', "None") != "None":
        tips_list.append("actors")
    if movie.get('description', ""):
        txt = movie.get('description', "").replace(".", '').replace("*", '')
        if len(txt) > 10:
            tips_list.append("text")
    roll = random.choice(tips_list)

    res = None
    if roll == "screen":
        res = next_screen(movie)
        if points >= 6:
            set_points(points - 5)
    if roll == "text":
        res = next_text(movie)
        if points >= 4:
            set_points(points - 3)
    if roll == "actors":
        res = "В ролях: " + str(movie['actors'])
        movie['actors'] = None
        save_mv(movie)
        if points >= 2:
            set_points(points - 1)
    if roll == "genre":
        res = "Жанры: " + str(movie['genre'])
        movie['genre'] = None
        save_mv(movie)
        if points >= 2:
            set_points(points - 1)
    return res


def get_game_users():
    if not os.path.exists("user_points.yaml"):
        return {}

    with open("user_points.yaml", "r") as f:
        res = f.read()
        j_res = yaml.load(res)
        return j_res


def upd_game_users(res):
    with open("user_points.yaml", "w") as f:
        f.write(str(res))
        return res


def add_points_to_user(user):
    p = get_points()
    res = get_game_users()
    cur_points = int(res.get(user, 0))
    res[user] = cur_points + p
    result = upd_game_users(res)
    return result
