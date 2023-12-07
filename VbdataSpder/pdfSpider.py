import time
import json
import hashlib
import requests
from loguru import logger


# 登录之后接口有这两个参数，如果不带的话只能看前几页
user_key = 'xxxx'
uuid = 'xxxx'

headers = {
    "authority": "vcbeat-vbdata-api.vbdata.cn",
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "application/json; charset=UTF-8",
    "origin": "https://vbdata.cn",
    "referer": "",
    "sign": "",
    "timestamp": "",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}


def get_sign(data):
    time_date = str(time.time() * 1000).split('.')[0]

    data_str = (json.dumps(data)).replace(' ', '') + time_date
    obj = hashlib.md5()
    obj.update(data_str.encode('utf-8'))
    sign = obj.hexdigest()

    return sign, time_date


# 详情页同样也需要保持时间戳、data等一致才能成功
def request_detail_api(uid):
    data = {
        "uid": uid,
        "user_key": user_key,
        "uUid": uuid,
        "uUserId": 100721
    }
    decrypt_data = get_sign(data)

    headers['referer'] = 'https://vbdata.cn/reportDetail/{}'.format(uid)
    headers['sign'] = decrypt_data[0]
    headers['timestamp'] = decrypt_data[1]

    url = 'https://vbdata.cn/dg/reportdetail'

    cookies = {
        "UM_distinctid": "18bdb4658a044c-06b68b7de36df6-26021d51-1fa400-18bdb4658a1154c",
        "uuid": uuid,
        "user_key": user_key,
        "timestamp_left": decrypt_data[1],
        "timestamp_right": "decrypt_data[1]",
        "acw_tc": "76b20f6617002020076683177e21ba02930cd966abbcc7080c59411af853cc",
        "CNZZDATA1279030029": "1150489486-1700190902-%7C1700203041"
    }

    new_data = json.dumps(data, separators=(',', ':'))
    response = requests.post(url, headers=headers, data=new_data, cookies=cookies)

    pdf = 'https://cdn.vcbeat.top' + response.json()['res'][0]['file_path']

    return pdf


def request_vbdata_api():
    for p in range(1, 301):
        items = []
        data = {
            "page": p,
            "keyword": "",
            "app_layer_tag": 0,
            "type": 0,
            "year": 0,
            "user_key": user_key,
            "uUid": uuid,
            "uUserId": 100721
        }
        decrypt_data = get_sign(data)

        headers['referer'] = 'https://vbdata.cn'
        headers['sign'] = decrypt_data[0]
        headers['timestamp'] = decrypt_data[1]

        url = "https://vcbeat-vbdata-api.vbdata.cn/report/getReportList"

        new_data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, data=new_data)

        for result in response.json()['data']:
            pdf = request_detail_api(result['uid'])
            logger.info('title：{}'.format(result['title']))
            logger.success('pdf链接：{}'.format(pdf, result['uid']))


if __name__ == '__main__':
    request_vbdata_api()
