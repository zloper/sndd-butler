import random

import requests
import re

import yaml

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

        url = f"{base}search/title?release_date={start_year}-01-01,2018-12-31&user_rating=,10.0&num_votes=100,&genres={mv_type}&companies={company}&view=simple&count=250"

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

    mv_info["title"] = [title, orig_title, parent_title]

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
    mv = get_random_movie(easy_mod=easy_mod)
    movie = parse_film(mv)
    scrn = get_and_rm_screen(movie)
    res = open_screen(scrn)
    return res


def next_screen():
    movie = get_mv()
    if movie == {}:
        print("game not exist")
        return

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
