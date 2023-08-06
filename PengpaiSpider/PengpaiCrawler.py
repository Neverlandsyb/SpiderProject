import json
import time
import random
import requests
import datetime
import logging
from lxml import etree


class PengPaiCrawler:
    """
    澎湃新闻类
    """
    # 日志
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s:%(message)s")

    # 初始化
    def __init__(self):
        # 今天时间
        self.TODAY = datetime.datetime.now().strftime("%Y-%m-%d") + " 23:59:59"
        # 把今天的时间转化为时间戳
        self.START_TIME = self.date_to_timestamp(self.TODAY)
        self.PAGESIZE = 100
        self.HEADERS = {
            "Accept": "application/json",
            "Referer": "https://www.thepaper.cn/",
            "Origin": "https://www.thepaper.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            "Content-Type": "application/json"
        }
        # POST请求参数,类型为国际
        self.DATA = {
            "nodeId": "25429",
            "excludeContIds": [],
            "pageSize": self.PAGESIZE,
            "startTime": "",
            "pageNum": 1
        }
        self.URL = "https://api.thepaper.cn/contentapi/nodeCont/getByNodeIdPortal"
        self.DETAIL_URL = "https://www.thepaper.cn/newsDetail_forward_"
        # 接口的最后时间
        self.FINAL_TIME = ""
        self.INDEX = 0
        self.FILE = open("PengPai_News.json", "a+", encoding="utf-8")

    # 把日期转换为时间戳
    @staticmethod
    def date_to_timestamp(dt):
        time_array = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
        timestamp = time.mktime(time_array)

        # 给格式化后的时间戳添加上随机数
        num = random.randint(1000, 9999)
        start_time = int(timestamp * 1000) + num

        return start_time

    # 把时间戳转换成时间
    @staticmethod
    def timestamp_to_date(dt):
        time_local = time.localtime(int(dt / 1000))
        date = time.strftime("%Y-%m-%d %H:%M:%S", time_local)

        return date

    def parser(self, data):
        """
        数据解析
        :param data:
        :return:
        """
        response = requests.post(self.URL, headers=self.HEADERS, data=json.dumps(data))

        if len(response.json()["data"]["list"]) == 1:
            logging.info("Crawler completed!")
            exit()
        else:
            for result in response.json()["data"]["list"]:
                detail_url = self.DETAIL_URL + str(result["contId"])
                publish_time = self.timestamp_to_date(result["pubTimeLong"])
                title = result["name"]

                self.FINAL_TIME = publish_time

                try:
                    details = self.get_details(detail_url)
                    if details[1] == "":
                        text_type = "图片或视频"
                    else:
                        text_type = "文本"

                    json_data = {
                        "text_type": text_type,
                        "person": details[0],
                        "publish_time": publish_time,
                        "url": detail_url,
                        "title": title,
                        "text": details[1],
                    }
                except Exception as e:
                    json_data = {
                        "text_type": "外链",
                        "publish_time": publish_time,
                        "url": result["link"],
                        "title": title,
                    }
                    logging.error("Error!{}".format(repr(e)))

                json_form = json.dumps(json_data, ensure_ascii=False, indent=2)
                self.FILE.write(json_form + "\n")

                self.INDEX += 1
                logging.info("Url is：{}，publish time is：{}".format(detail_url, publish_time))

            logging.info("Spider is running，{} items have been caught!".format(self.INDEX))

    # 抓取当天的新闻数据，然后返回最后一天的时间
    def crawler(self):
        if self.FINAL_TIME == "":
            self.DATA["startTime"] = self.START_TIME
            self.parser(self.DATA)
            time.sleep(2)
            return self.crawler()
        else:
            self.DATA["startTime"] = self.date_to_timestamp(self.FINAL_TIME)
            self.parser(self.DATA)
            time.sleep(2)
            return self.crawler()

    # 新闻详情,提取详细数据
    def get_details(self, detail_url):
        detail_response = requests.get(detail_url, headers=self.HEADERS)
        detail_html = etree.HTML(detail_response.text)
        person = detail_html.xpath("*//div[@class='index_left__LfzyH']/div/text()")
        text = detail_html.xpath("*//div[@class='index_cententWrap__Jv8jK']/p//text()")

        result = ""
        for node in text:
            result += node.replace("\u3000", "")

        time.sleep(2)

        return person[0], result


if __name__ == '__main__':
    Spider = PengPaiCrawler()
    Spider.crawler()
