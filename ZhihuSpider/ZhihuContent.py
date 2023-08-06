import re
import time
import json
import execjs
import random
import logging
import requests
import pymysql


class TypeCrawler:
    """
    知乎各类型id爬虫类
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s:%(message)s")

    def __init__(self):
        # 话题广场
        self.TOPICS = [1761, 3324, 833, 99, 69, 113, 304, 13908, 570, 2955, 988, 388, 285, 686, 444, 1537, 19800,
                       253, 4196, 8437, 2253, 4217, 2143, 1538, 1740, 237, 112, 445, 1027, 215, 68, 75, 395]
        # 类型页面限制
        self.TYPE_PAGE = 50

        # 初始url
        self.DOMAIN_URL = "https://www.zhihu.com"
        self.URL = "https://www.zhihu.com/node/TopicsPlazzaListV2"
        self.DETAIL_URL = "/api/v5.1/topics/{}/feeds/{}?offset={}&limit=10&"
        # API类型
        self.API_TYPE = ["essence", "timeline_activity", "top_activity", "top_question", "new_question"]

        # 取cookie中的d_c0,构造多一点cookie防止被封
        self.D_C0 = [
            "xxxx",
            "xxxx"
        ]

        self.HEADERS = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        self.SESSION = requests.session()
        self.TOPICS_DATA = {
            "method": "next",
            "params": ""
        }
        # 详情Json的标识以及页面限制
        self.IS_END = False
        self.PAGE = 100
        # 构建一个列表三元组
        self.PAGE_TOP_API = []
        # 构建一个标识集合,存放类型id和api
        self.FLAG = set()

        # 连接数据库
        self.CONN = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="syb1022.",
            db="data_set",
        )

        self.CUR = self.CONN.cursor()

    @staticmethod
    def timestamp_to_date(dt):
        """
        时间戳转换成日期
        :param dt:
        :return:
        """
        time_local = time.localtime(int(dt))
        date = time.strftime("%Y-%m-%d %H:%M:%S", time_local)

        return date

    def get_type_id(self):
        """
        抓取知乎话题广场所有类型的id
        :return: File
        """
        sql = "INSERT INTO `data_set`.`zhihu_topic_data`(`topic_path_id`, `topic_url`, `topic_name`, `create_time`) VALUES ('{}', '{}', '{}', '{}')"

        for topic in self.TOPICS:
            for offset in range(0, self.TYPE_PAGE):
                self.TOPICS_DATA["params"] = json.dumps({"topic_id": topic, "offset": offset * 20, "hash_id": ""})
                response = self.SESSION.post(self.URL, headers=self.HEADERS, data=self.TOPICS_DATA)
                result = response.json()["msg"]
                topic_id = re.findall('href="/topic/(.*?)"', str(result))
                topic_name = re.findall('alt="(.*?)"', str(result))
                print(topic_name)
                if topic_id:
                    for t in range(len(topic_id)):
                        topic_url = "https://www.zhihu.com/topic/{}/hot".format(topic_id[t])
                        self.CUR.execute(sql.format(topic, topic_url, topic_name[t], "2023-07-15"))
                        self.CONN.commit()
                else:
                    break
            time.sleep(2)

        self.CUR.close()
        self.CONN.close()

    def get_headers(self, api):
        """
        爬虫请求头参数构造
        :param api:
        :return: self.Headers
        """
        d_c0 = random.choice(self.D_C0)
        with open("X-Zse-96.js", "r", encoding="utf-8") as f:
            js = f.read()

        etx = execjs.compile(js)
        x_zse_96 = etx.call("get_xzse96", d_c0, api)

        self.HEADERS["cookie"] = "d_c0={};".format(d_c0)
        self.HEADERS["x-zse-96"] = x_zse_96
        self.HEADERS["x-api-version"] = "3.0.91"
        self.HEADERS["x-zse-93"] = "101_3_3.0"

    def get_question(self):
        """
        抓取知乎Json数据的问题
        """
        topics_file = open("topic_id_name.txt", "r", encoding="utf-8")
        topics = [i.strip() for i in topics_file]

        # 把类型id去重
        topics = list(set(topics))

        for page in range(0, self.PAGE + 1):
            for top in topics:
                for api in self.API_TYPE:
                    top_id = top.split("\t")[1]
                    self.PAGE_TOP_API.append((page, top_id, api))

        for tup in self.PAGE_TOP_API:
            # 重组类型id和api
            flag = (tup[1], tup[2])
            if flag in self.FLAG:
                print("此id已抓完", flag[1])
                pass
            else:
                print(tup)
                url = self.DOMAIN_URL + self.DETAIL_URL.format(tup[1], tup[2], tup[0])
                self.get_headers(api=self.DETAIL_URL.format(tup[1], tup[2], tup[0]))

                response = self.SESSION.get(url, headers=self.HEADERS)
                self.parser(tup[1], tup[2], response.json())
            time.sleep(5)

    def parser(self, top_id, type_api, json_data):
        """
        解析Json数据
        :param top_id: 类型id
        :param type_api: 每个详情页的5个api
        :param json_data: Json数据
        :return: File
        """
        # 判断有没有下一页,如果IS_END是True的话,就没有下一页,则把类型id和api放入标识列表
        self.IS_END = json_data["paging"]["is_end"]

        if self.IS_END:
            self.FLAG.add((top_id, type_api))

        # 取数据
        for data in json_data["data"]:
            try:
                target = data["target"]
                result = re.findall("'title': '(.*?)'", str(target))
                title = result[-1]
                print(title)
            except Exception as e:
                print(repr(e))

    def get_question_token_data(self):
        """
        获取问题token以及其他信息
        可以通过token抓取评论
        :return:
        """
        sql = "SELECT * FROM `data_set`.`zhihu_topic_data` "
        self.CUR.execute(sql)
        topic_data = self.CUR.fetchall()
        for topic in topic_data:
            print(topic[2].split("/")[-2])
            topic_id = topic[2].split("/")[-2]
            params_to_decrypt = self.DETAIL_URL.format(topic_id, "essence", "0")
            comment_api = self.DOMAIN_URL + params_to_decrypt
            print(comment_api)
            self.get_headers(params_to_decrypt)

            comment_response = self.SESSION.get(comment_api, headers=self.HEADERS)

            for data in comment_response.json()["data"]:
                try:
                    question_token = data["target"]["token"]
                    target = data["target"]["question"]
                    print(question_token, target["id"], target["title"], target["url"])
                except Exception as e:
                    print(repr(e))
            time.sleep(10)

        self.CUR.close()
        self.CONN.close()


if __name__ == '__main__':
    TypeSpider = TypeCrawler()
    # TypeSpider.get_question()
    # TypeSpider.get_type_id()
    TypeSpider.get_question_token_data()
