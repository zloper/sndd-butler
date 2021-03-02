import json

import requests


def finder(message):
    msg = message.content.lower().split("сая!")[1].strip()

    # if msg.startswith("давай edm"):
    #     get_coub()

    if msg.startswith("давай аниме"):
        url = "https://coub.com/api/v2/timeline/random/anime?page=1"
        r = requests.get(url)
        txt = r.text

        dct = json.loads(txt)['coubs'][0]
        res = 'https://coub.com/view/%s' % dct['permalink']

        # print(dct)
        # print(dct['file_versions'])
        # print(dct['file_versions']['html5'])
        
        id = str(message.guild)
        if id == "None":
            id = message.author

        audio = dct['file_versions']['html5']['audio']
        set_track(audio['high']['url'], id)
        return res

    if msg.startswith("скинь трек"):
        id = str(message.guild)
        if id == "None":
            id = message.author

        res = get_track(id)
        return res


def get_coub(url,msg):
    r = requests.get(url)
    txt = r.text

    dct = json.loads(txt)['coubs'][0]
    res = 'https://coub.com/view/%s' % dct['permalink']

    # print(dct)
    # print(dct['file_versions'])
    # print(dct['file_versions']['html5'])

    id = str(msg.guild)
    if id == "None":
        id = msg.author

    audio = dct['file_versions']['html5']['audio']
    set_track(audio['high']['url'], id)
    return res


def set_track(txt, server):
    with open('%s_tmp_track.log' % server, 'w') as f:
        f.write(txt)


def get_track(server):
    with open('%s_tmp_track.log' % server, 'r') as f:
        txt = f.read()
        return txt
