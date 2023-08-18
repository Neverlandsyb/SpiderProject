import execjs
import requests


def get_access_key():
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://www.shubl.com",
        "Referer": "https://www.shubl.com/chapter/book_chapter_detail/102415473",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",

    }

    url = "https://www.shubl.com/chapter/ajax_get_session_code"
    data = {
        "chapter_id": "100991386"
    }
    response = res.post(url, headers=headers, data=data)

    print(response.json()["chapter_access_key"])

    return response.json()["chapter_access_key"]


def get_detail():
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://www.shubl.com",
        "Referer": "https://www.shubl.com/chapter/book_chapter_detail/102415473",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",

    }

    url = "https://www.shubl.com/chapter/get_book_chapter_detail_info"

    access_key = get_access_key()
    data = {
        "chapter_id": "100991386",
        "chapter_access_key": access_key
    }
    response = res.post(url, headers=headers, data=data)
    # print(response.json())

    # print(response.json()["chapter_content"])
    # print(response.json()["encryt_keys"])

    g = {
        "content": response.json()["chapter_content"],
        "keys":response.json()["encryt_keys"],
        "accessKey":access_key
    }
    js_file = open("shudan.js", "r").read()
    result = execjs.compile(js_file).call("decrypt", g)

    print(result)


if __name__ == '__main__':
    res = requests.Session()
    get_detail()
