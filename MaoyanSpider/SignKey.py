import hashlib
import random
import re
import time
import requests


def date_to_timestamp():
    """
    1.把日期转换为时间戳
    2.给格式化后的时间戳添加上随机数
    """
    dt = time.strftime("%Y-%m-%d %H:%M:%S")
    time_array = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(time_array)

    num = random.randint(1000, 9999)
    start_time = int(timestamp * 1000) + num

    return start_time


def get_movie_id(offset):
    """
    获取电影id
    :param offset: Max
    :return:
    """
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Set-Cookie": "uid.sig=hlqKwItixnwRJMmu6X-sP8X3qa8; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; httponly",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    }
    url = "https://www.maoyan.com/films?yearId=15&showType=3&offset={}".format(30 * offset)
    response = requests.get(url, headers=headers)

    movie = re.findall('<a href="/films/.*?" target="_blank" data-act="movies-click" data-val="{movieId:(.*?)}">.*?</a>',response.text)

    return movie


def get_params(movieId):
    """
    详情页uuid必须要
    :param movieId:
    :return:
    """
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
        "Accept": "*/*",
        "Referer": "https://www.maoyan.com/films/1305801",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }
    cookies = {
        "uuid": "73014560245411EEB2FC317045D56AC23DABC3FC6A7645399A74960B5074C920",
    }
    ts = int(time.time() * 1000)
    index = int(10 * random.random())

    u = "&key=A013F70DB97834C0A5492378BD76C53A"
    c = "method=GET&timeStamp={}&User-Agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36&index={}&channelId=40011&sVersion=1".format(
        ts, index)
    keys = c + u
    sign_key = hashlib.md5(keys.encode(encoding="utf-8")).hexdigest()

    print(index, ts, sign_key)
    params = {
        "timeStamp": ts,
        "index": index,
        "signKey": sign_key,
        "channelId": 40011,
        "sVersion": 1,
        "webdriver": "false"
    }

    url = "https://www.maoyan.com/ajax/films/{}?".format(movieId)
    response = requests.get(url, headers=headers, params=params, cookies=cookies)
    print(response.text)

    time.sleep(100)


if __name__ == '__main__':
    # 第一页
    page = 0
    movie_id = get_movie_id(page)
    print(movie_id)
    for i in movie_id:
        get_params(i)
