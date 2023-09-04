import re
import time
import random
import requests
from lxml import etree
from urllib.parse import quote
from requests.utils import dict_from_cookiejar


class SogouSearch:
    """
    搜索微信爬虫
    """

    def __init__(self, main_url):
        self.SUV_URL = "https://pb.sogou.com/pv.gif?"
        self.HEADERS = {
            "Cookie": "",
            "Host": "weixin.sogou.com",
            "Connection": 'keep-alive',
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        self.URL = main_url
        self.WX_HEADERS = {
            "Accept-Encoding": 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        }

    def get_suv(self):
        """
        获取cookie中的suv
        :return:
        """
        response = requests.get(self.SUV_URL, headers=self.HEADERS)
        suv_id = dict_from_cookiejar(response.cookies)["SUID"]
        self.HEADERS["Cookie"] = "SUID=" + suv_id
        print(self.HEADERS)

    def get_sogou_url(self):
        """
        获取搜狗中转链接
        :return:
        """
        self.get_suv()
        self.HEADERS["Referer"] = self.URL
        main_url_res = requests.get(self.URL, headers=self.HEADERS)

        set_cookies = main_url_res.headers["Set-Cookie"].split(";")

        cookie_list = []
        for ck in set_cookies:
            if "SNUID" in ck or "SUID" in ck:
                cookie_list.append(ck)

        self.HEADERS["Cookie"] = (self.HEADERS["Cookie"] + ";".join(cookie_list)).replace(" path=/, ", "")

        main_html = etree.HTML(main_url_res.text)
        urls = main_html.xpath("*//div[@class='txt-box']/h3/a/@href")

        for m in urls:
            b = int(random.random() * 100) + 1
            a = m.find("url=")
            link = "https://weixin.sogou.com" + m + "&k=" + str(b) + "&h=" + m[a + 4 + 21 + b: a + 4 + 21 + b + 1]
            self.get_true_url(link)

    def get_true_url(self, sg_url):
        """
        获取真正的微信链接,并且解析获取详细数据
        :param sg_url:
        :return:
        """
        response = requests.get(sg_url, headers=self.HEADERS)
        url_content = re.findall("\'(\S+?)\';", response.text, re.S)

        true_url = "".join(url_content).replace("&from=inner", "")
        wx_response = requests.get(true_url, headers=self.WX_HEADERS)
        print(wx_response.text)
        wx_html = etree.HTML(wx_response.text)

        title = wx_html.xpath("*//h1[@id='activity-name']/text()")
        author_info = wx_html.xpath("//div[@id='meta_content']//text()")
        content = wx_html.xpath("*//div[@id='js_content']//text()")

        print(title)
        print(author_info)
        print(content)
        time.sleep(5)


if __name__ == '__main__':
    key = "蔡徐坤"
    url = "https://weixin.sogou.com/weixin?ie=utf8&s_from=input&_sug_=y&_sug_type_=&type=2&query={}".format(quote(key))
    WxSpider = SogouSearch(url)
    WxSpider.get_sogou_url()
