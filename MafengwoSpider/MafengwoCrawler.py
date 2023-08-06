import re
import time
import json
import execjs
import requests
import hashlib
import logging
from lxml import etree
from requests.utils import add_dict_to_cookiejar


class MafengwoSpider:
    """
    马蜂窝爬虫类
    """
    # 日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s:%(message)s')

    # 初始化
    def __init__(self):
        # 热门目的地网址
        self.URL_MDD = "https://www.mafengwo.cn/mdd/"
        # 目的地景点网址
        self.URL_ROUTE = "https://www.mafengwo.cn/ajax/router.php"
        # 景点详细地址
        self.URL_DETAIL = "https://www.mafengwo.cn"
        # 统一请求头
        self.HEADERS = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://www.mafengwo.cn/"
        }
        # 会话
        self.RES = requests.session()
        # 景点页码
        self.PAGE_TOTAL = 1
        # 时间戳
        self.TS = int(time.time() * 1000)

    # 获取所有热门目的地ID列表
    def get_city_id(self):
        response = self.RES.get(self.URL_MDD, headers=self.HEADERS)

        # 解析网页取出所有热门景点
        html = etree.HTML(response.text)

        # 分两种:1.省份或国家 2.地区 然后相加并去重
        scenic_spot1 = html.xpath("*//dl/dt/a/@href")
        scenic_spot2 = html.xpath("*//dl/dd/a/@href")
        scenic_spot_total = list(set(scenic_spot1 + scenic_spot2))

        cities = []
        for c in scenic_spot_total:
            city_id = c.split("/")
            cities.append(city_id[-1])

        return cities

    # 解密_sn参数,md5加密
    def get_params(self, city_id, page):
        # 构造参数
        params = f'{{"_ts":"{self.TS}","iMddid":"{city_id}","iPage":"{page}","iTagId":"0","sAct":"KMdd_StructWebAjax|GetPoisByTag"}}'

        # 加盐
        salt = 'c9d6618dbc657b41a66eb0af952906f1'

        m = hashlib.md5()
        m.update((params + salt).encode())

        # 解密
        _sn = m.hexdigest()[2:12]

        return _sn

    # 获取每个景点的url组成列表,这里为演示省时,先只取一个地区id,如有需求就把上面的cities传过来
    def get_detail_url(self):
        city_id = 10065
        scenic_spot_detail_url = []

        for page in range(1, self.PAGE_TOTAL + 1):
            data = {
                "_ts": self.TS,
                "iMddid": city_id,  # 这里定死了,如有需求可自行修改
                "iPage": page,
                "iTagId": "0",
                "sAct": "KMdd_StructWebAjax|GetPoisByTag",
                "_sn": self.get_params(city_id, page)
            }

            # 注意这里请求是post
            response = self.RES.post(self.URL_ROUTE, headers=self.HEADERS, data=data)

            # 用正则获取子链接
            href = re.findall('href="(.*?)"', str(response.json()))
            scenic_spot_detail_url += href

            # 睡眠时间自己把握
            time.sleep(2)

        logging.info("detail data length : %s", len(scenic_spot_detail_url))

        return scenic_spot_detail_url

    # 整理详情
    @staticmethod
    def text_collation(data):
        result = ""
        for r in data:
            result += r.strip().replace(" ", "")

        return result

    # 获取景点详情
    def get_detail_data(self):
        # 获取热门景点列表
        scenic_spot_detail_url = self.get_detail_url()

        for url in scenic_spot_detail_url:
            # 解析,组合详情url
            url = self.URL_DETAIL + url
            response = self.get_html(url)

            logging.info("crawling detail url : {}, response : {}".format(url, response.status_code))

            html = etree.HTML(response.text)
            # 标题
            spot = html.xpath("*//h1/text()")
            # 景点介绍
            summary = html.xpath("*//div[@class='summary']/text()")
            # 联系方式
            tel = html.xpath("*//ul[@class='baseinfo clearfix']/li[@class='tel']/div[@class='content']/text()")
            # 交通
            traffic = html.xpath("*//div[@class='mod mod-detail']/dl[1]/dd//text()")
            # 门票
            ticket = html.xpath("*//div[@class='mod mod-detail']/dl[2]/dd//text()")
            # 开放时间
            open_time = html.xpath("*//div[@class='mod mod-detail']/dl[3]/dd//text()")

            # 写入json,这里是全爬完再写入,可自行修改
            json_dict = dict()
            json_dict["spot"] = self.text_collation(spot)
            json_dict["summary"] = self.text_collation(summary)
            json_dict["tel"] = self.text_collation(tel)
            json_dict["traffic"] = self.text_collation(traffic)
            json_dict["ticket"] = self.text_collation(ticket)
            json_dict["open_time"] = self.text_collation(open_time)

            item_list.append(json_dict)

            time.sleep(3)

        with open("mfw_data.json", "a+", encoding="utf-8") as file:
            json.dump(item_list, file, ensure_ascii=False, indent=2)

    # 详情页面cookie反爬
    def get_html(self, detail_url):
        try:
            # 第一次请求,获取js代码
            r1 = self.RES.get(detail_url, headers=self.HEADERS, verify=False)

            js_code = re.findall('cookie=(.*?);location', r1.text)[0]

            # 反混淆、分割出cookie的部分
            ck1 = execjs.eval(js_code).split(";")[0].split("=")[1]

            # 第二次请求,将第一次访问的cookie添加进入session会话中
            add_dict_to_cookiejar(self.RES.cookies, {"__jsl_clearance_s": ck1})
            r2 = self.RES.get(detail_url, headers=self.HEADERS, verify=False)

            # 取出go值
            ck2 = json.loads(re.findall(r"};go\((.*?)\)</script>", r2.text)[0])

            # 判断并构造cookie
            for i in range(len(ck2['chars'])):
                for j in range(len(ck2['chars'])):
                    values = ck2['bts'][0] + ck2['chars'][i] + ck2['chars'][j] + ck2['bts'][1]
                    if ck2['ha'] == 'md5':
                        ha = hashlib.md5(values.encode()).hexdigest()
                    elif ck2['ha'] == 'sha1':
                        ha = hashlib.sha1(values.encode()).hexdigest()
                    elif ck2['ha'] == 'sha256':
                        ha = hashlib.sha256(values.encode()).hexdigest()
                    if ha == ck2['ct']:
                        __js_code = values

            add_dict_to_cookiejar(self.RES.cookies, {"__jsl_clearance_s": __js_code})

            # 第三次请求得出html
            result = self.RES.get(detail_url, headers=self.HEADERS, verify=False)
        except Exception as e:
            result = self.RES.get(detail_url, headers=self.HEADERS, verify=False)
            logging.info("cookie is existed!!!")

        return result


if __name__ == '__main__':
    item_list = []
    Crawler = MafengwoSpider()
    Crawler.get_detail_data()
