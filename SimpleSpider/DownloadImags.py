import json
import time
import execjs
import requests


def get_image_id():
    headers = {
        "authority": "api.zzzmh.cn",
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://bz.zzzmh.cn",
        "referer": "https://bz.zzzmh.cn/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    url = "https://api.zzzmh.cn/bz/v3/getData"

    data = {
        "category": 0,
        "categoryId": 0,
        "color": 0,
        "current": 1,
        "ratio": 0,
        "resolution": 0,
        "size": 24,
        "sort": 0
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    encrypt_data = response.json()["result"]
    file = open("image_decrypt.js", "r").read()

    json_data = json.loads(execjs.compile(file).call("_0x563330", encrypt_data))

    for data in json_data["list"]:
        i = data["i"]
        t = data["t"]
        # 拼接图片id
        image_id = i + str(t) + "9"
        image_redirect_url = "https://api.zzzmh.cn/bz/v3/getUrl/" + image_id

        # 获取真正的原图下载地址
        redirect_response = requests.get(image_redirect_url, headers=headers, allow_redirects=False)
        content_url = redirect_response.headers["Location"]
        print(content_url)

        image_content = requests.get(content_url, headers=headers)
        with open(f"{image_id}.jpg", "wb") as file:
            file.write(image_content.content)
        print(f"{image_id} 图片下载完成")
        time.sleep(2)


if __name__ == '__main__':
    get_image_id()
