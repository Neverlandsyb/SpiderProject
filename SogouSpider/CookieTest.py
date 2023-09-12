import requests


def get_new_cookies():
    """
    搜狗视频cookies、搜狗系cookies通用
    :return:
    """
    url = "https://v.sogou.com/?forceredirect=2&ie=utf8"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    cookies = response.cookies.get_dict()
    return cookies


def get_sogou_mp(url):
    """
    获取搜狗微信链接详情
    :param url:
    :return:
    """
    headers = {
        "Referer": "https://www.baidu.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    cookies = get_new_cookies()
    response = requests.get(url, headers=headers, cookies=cookies)

    return response.text
  
