import re
import os
import time
import requests

class BaiKeRelationSpider:
    """
    百科知识图谱爬虫
    """
    def __init__(self, name, lemma_id):
        """
        参数说明
        NAME:电视剧名字
        LEMMA_ID:电视剧百科ID
        MAIN_URL:电视剧的百科详情页
        LEMMA_GRAPH_URL:总图谱API
        """
        self.NAME = name
        self.LEMMA_ID = lemma_id
        self.MAIN_URL = "https://baike.baidu.com/item/{}/{}".format(self.NAME, self.LEMMA_ID)
        self.SESSION = requests.session()

        self.HEADERS = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        }
        self.LEMMA_GRAPH_URL = "https://baike.baidu.com/lemmagraph/api/getfeaturegraph?"
        self.ACTOR_DETAIL_URL = "https://baike.baidu.com/lemmagraph/api/getlemmadetail?"
        self.FEATURE_ID = self.get_feature_id()

        self.IMAGE_FILE_PATH = "./character_avatar"

    def get_feature_id(self):
        """
        在百科详情页里获取featureId参数
        :return: featureId
        """
        item_response = self.SESSION.get(self.MAIN_URL, headers=self.HEADERS)
        item_response.encoding = "utf-8"

        feature_id = re.findall('"featureId":"(.*?)"', item_response.text)

        print("feature_id：", feature_id[0])

        return feature_id[0]

    def get_actor_details(self, lemma_id):
        """
        获取角色名已经演员详细信息
        :return: tuple
        """
        params = {
            "lemmaId": lemma_id,
            "featureId": self.FEATURE_ID,
            "type": "roleDetail"
        }
        response = self.SESSION.get(self.ACTOR_DETAIL_URL, headers=self.HEADERS, params=params)

        try:
            character_name = response.json()["data"]["base"]["jumpLemmaTitle"]
        except Exception as e:
            repr(e)
            character_name = "None"

        try:
            character_summary = response.json()["data"]["base"]["summary"]
        except Exception as e:
            repr(e)
            character_summary = "None"

        try:
            actor_name = response.json()["data"]["relatedList"][0]["lemmaTitle"]
        except Exception as e:
            repr(e)
            actor_name = "None"

        try:
            actor_summary = response.json()["data"]["relatedList"][0]["summary"]
        except Exception as e:
            repr(e)
            actor_summary = "None"

        return character_name, character_summary, actor_name, actor_summary

    def get_triplets(self):
        """
        获取知识图谱三元组信息、图片
        :return: tuple
        """
        params = {
            "lemmaId": self.LEMMA_ID,
            "pn": 1,
            "rn": 50,
            "withModule": 1,
            "featureId": self.FEATURE_ID
        }
        response = self.SESSION.get(self.LEMMA_GRAPH_URL, headers=self.HEADERS, params=params)

        if not os.path.exists(self.IMAGE_FILE_PATH):
            os.mkdir(self.IMAGE_FILE_PATH)

        actor_dict = dict()

        for data in response.json()["data"]["recommend"]:
            with open(self.IMAGE_FILE_PATH + "/{}.jpg".format(data["lemmaTitle"]), "wb") as fp:
                fp.write(self.SESSION.get(data["coverPic"], headers=self.HEADERS).content)

            actor_info = self.get_actor_details(data["lemmaId"])
            print(actor_info)
            actor_dict[data["id"]] = {
                "lemmaId": data["lemmaId"],
                "lemmaTitle": data["lemmaTitle"],
                "itemDesc": data["itemDesc"],
                "character_summary": actor_info[1],
                "actor_name": actor_info[2],
                "actor_summary": actor_info[3]
            }
            time.sleep(1)

        print(actor_dict)

        relation_list = []

        for relation in response.json()["data"]["edges"]:
            try:
                trp = dict()
                source = actor_dict[relation["source"]]
                target = actor_dict[relation["target"]]

                trp["source"] = (source["lemmaTitle"])
                trp["target"] = (target["lemmaTitle"])

                trp["relation"] = relation["relationName"]
                trp["direction"] = relation["direction"]

                triplet_dict = {
                    "source": (
                        actor_dict[relation["source"]]["lemmaTitle"], actor_dict[relation["source"]]["itemDesc"],
                        actor_dict[relation["source"]]["character_summary"],
                        actor_dict[relation["source"]]["actor_name"], actor_dict[relation["source"]]["actor_summary"]),
                    "target": (
                        actor_dict[relation["target"]]["lemmaTitle"], actor_dict[relation["target"]]["itemDesc"],
                        actor_dict[relation["target"]]["character_summary"],
                        actor_dict[relation["target"]]["actor_name"], actor_dict[relation["target"]]["actor_summary"]),
                    "relation": relation["relationName"],
                    "direction": relation["direction"]
                }

                relation_list.append(triplet_dict)
            except Exception as e:
                print(repr(e))

        print(relation_list)


if __name__ == '__main__':
    movie = "长相思"
    movie_id = 6266895

    Spider = BaiKeRelationSpider(movie, movie_id)
    Spider.get_triplets()
