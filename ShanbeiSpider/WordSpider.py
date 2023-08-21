import json
import execjs
import requests

def get_data(book_id):
    headers = {
        "Access-Control-Request-Method": "GET",
        "Origin": "https://web.shanbay.com",
        "Referer": "https://web.shanbay.com/wordsweb/",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
        "Access-Control-Request-Headers": "x-csrftoken",
        "Accept": "application/json, text/plain, */*",
        "X-CSRFToken": "oN2T8dqLwmBjo2fE9BNRFGO9VTx334rF"
    }
    cookies = {
        "auth_token": "xxxx"
    }
    url = "https://apiv3.shanbay.com/wordsapp/user_material_books/{}/learning/words/unlearned_items".format(book_id)
  
    params = {
        "ipp": "10",
        "page": "1"
    }
    response = requests.get(url, headers=headers, params=params, cookies=cookies)
    encrypt_data = response.json()["data"]
  
    json_data = json.loads(execjs.compile(open("decode.js", "r").read()).call("decry", encrypt_data))
    for data in json_data["objects"]:
        print(data)
        definition_cn = str(["" + i["definition_cn"] for i in data["vocab_with_senses"]["senses"]])
        word = data["vocab_with_senses"]["word"]
        word_id = data["vocab_with_senses"]["vocabulary_id"]
        audio_us_urls = str(data["vocab_with_senses"]["sound"]["audio_us_urls"])
        audio_uk_urls = str(data["vocab_with_senses"]["sound"]["audio_uk_urls"])


if __name__ == '__main__':
    book = "rcdtq" # 完全版考研考纲词汇(顺序)
    get_data(book)
  
