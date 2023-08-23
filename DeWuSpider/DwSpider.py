import execjs
import requests


class DwSpider:
    """
    得物爬虫
    """

    def __init__(self):
        self.INDEX_URL = "https://app.poizon.com/api/v1/h5/index/fire/index"
        self.DETAIL_URL = "https://app.poizon.com/api/v1/h5/commodity/fire/recommend"
        self.HEADERS = {
             'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Origin': 'https://m.poizon.com',
            'Referer': 'https://m.poizon.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        }

    @staticmethod
    def get_sign(par):
        """
        获得sign值
        :return:
        """
        js_code = open("data_decrypt.js").read()
        sign = execjs.compile(js_code).call("get_sign", par)
        detail_sign = execjs.compile(js_code).call("get_detail_sign", par)

        return sign, detail_sign

    def get_data(self, page):
        """
        获取商品列表
        :param page:
        :return:
        """
        json_data = {
            "sign": self.get_sign(page)[0],
            "tabId": "",
            "limit": 20,
            "lastId": page,
            "platform": 'h5',
            "version": '4.73.0',
            "isVisitor": False,
            "newAdvForH5": True,
        }

        response = requests.post(self.INDEX_URL, headers=self.HEADERS, json=json_data)

        for data in response.json()["data"]["hotList"]:
            if data["typeId"] == 0:
                print(data["product"])
                self.get_details(data["product"]["spuId"])
            else:
                print("typeId:4")

    def get_details(self, spu):
        """
        获取详情数据
        :return:
        """
        data = {
            "abTests": [{"name": "515_yhj", "value": "3"}],
            "limit": 50,
            "sign": self.get_sign(spu)[1],
            "spuId": spu
        }
        response = requests.post(self.DETAIL_URL, headers=self.HEADERS, json=data)
        print(response.json())


if __name__ == '__main__':
    Spider = DwSpider()
    Spider.get_data(1)
           
      

