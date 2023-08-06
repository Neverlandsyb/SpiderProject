import random
import re
import os
import math
import time
import ffmpeg
import hashlib
import requests
from tqdm import tqdm
from urllib.parse import urlencode


class BILIBILIVideoSpider:
    """
    哔哩哔哩视频下载爬虫
    """

    def __init__(self, cookie, bv):
        self.BV = bv
        self.COOKIES = dict()
        self.FILE = "./video/"
        self.COOKIES["SESSDATA"] = cookie
        self.URL = "https://www.bilibili.com/video/{}"
        self.FFMPEG = r"E:\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"

        self.HEADERS = {
            "Referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        }

    def b_to_a(self):
        """
        Bv号转Av号
        :return: AvId
        """
        # 1.去除Bv号前的"Bv"字符
        bv_number1 = self.BV[2:]
        keys = {
            '1': '13', '2': '12', '3': '46', '4': '31', '5': '43', '6': '18', '7': '40', '8': '28', '9': '5',
            'A': '54', 'B': '20', 'C': '15', 'D': '8', 'E': '39', 'F': '57', 'G': '45', 'H': '36', 'J': '38', 'K': '51',
            'L': '42', 'M': '49', 'N': '52', 'P': '53', 'Q': '7', 'R': '4', 'S': '9', 'T': '50', 'U': '10', 'V': '44',
            'W': '34', 'X': '6', 'Y': '25', 'Z': '1',
            'a': '26', 'b': '29', 'c': '56', 'd': '3', 'e': '24', 'f': '0', 'g': '47', 'h': '27', 'i': '22', 'j': '41',
            'k': '16', 'm': '11', 'n': '37', 'o': '2',
            'p': '35', 'q': '21', 'r': '17', 's': '33', 't': '30', 'u': '48', 'v': '23', 'w': '55', 'x': '32',
            'y': '14',
            'z': '19'

        }

        # 2. 将key对应的value存入一个列表
        bv_number2 = []
        for index, ch in enumerate(bv_number1):
            bv_number2.append(int(str(keys[ch])))

        # 3. 对列表中不同位置的数进行*58的x次方的操作
        bv_number2[0] = int(bv_number2[0] * math.pow(58, 6))
        bv_number2[1] = int(bv_number2[1] * math.pow(58, 2))
        bv_number2[2] = int(bv_number2[2] * math.pow(58, 4))
        bv_number2[3] = int(bv_number2[3] * math.pow(58, 8))
        bv_number2[4] = int(bv_number2[4] * math.pow(58, 5))
        bv_number2[5] = int(bv_number2[5] * math.pow(58, 9))
        bv_number2[6] = int(bv_number2[6] * math.pow(58, 3))
        bv_number2[7] = int(bv_number2[7] * math.pow(58, 7))
        bv_number2[8] = int(bv_number2[8] * math.pow(58, 1))
        bv_number2[9] = int(bv_number2[9] * math.pow(58, 0))

        # 4.求出这10个数的合
        bv_sum = 0
        for i in bv_number2:
            bv_sum += i

        # 5. 将和减去100618342136696320
        bv_sum -= 100618342136696320

        # 6. 将sum 与177451812进行异或
        temp = 177451812

        return bv_sum ^ temp

    def get_video(self):
        """
        获取视频的title、video和audio
        :return: title、video、audio
        """
        av_number = self.b_to_a()
        url = self.URL.format("av" + str(av_number))

        response = requests.get(url, headers=self.HEADERS, cookies=self.COOKIES)

        accept_quality = re.findall('"accept_quality":\[(.*?)\]', response.text)
        qualities = accept_quality[0].split(",")

        title = re.findall('<h1 title="(.*?)"', response.text)
        print("链接：{}，标题：{}".format(url, title[0]))

        video = "None"
        audio = re.findall('"audio":\[\{"id":30280,"baseUrl":"(.*?)"', response.text)

        for quality in qualities:
            if quality == "80":
                video = re.findall('"video":\[\{"id":80,"baseUrl":"(.*?)"', response.text)
                break
            elif quality == "64":
                video = re.findall('\{"id":64,"baseUrl":"(.*?)"', response.text)
                break
            else:
                pass

        return title[0], video[0], audio[0]

    def download(self):
        """
        下载video和audio并将两者合并
        :return: mp4
        """
        video_info = self.get_video()
        host = video_info[1].split("/")[2]
        self.HEADERS["host"] = host
        print(self.HEADERS)

        if not os.path.exists(self.FILE):
            os.mkdir(self.FILE)

        video_response = requests.get(video_info[1], stream=True, headers=self.HEADERS)
        video_size = int(video_response.headers["Content-Length"]) / 1024 / 1024

        with open(self.FILE + "{}_video".format(video_info[0]) + ".flv", "wb") as f:
            for video in tqdm(iterable=video_response.iter_content(1024 * 1024), total=video_size, desc="正在下载视频",
                              unit="MB"):
                f.write(video)

        audio_response = requests.get(video_info[2], stream=True, headers=self.HEADERS)
        audio_size = int(audio_response.headers["Content-Length"]) / 1024 / 1024

        with open(self.FILE + "{}_audio".format(video_info[0]) + ".flv", "wb") as fp:
            for audio in tqdm(iterable=audio_response.iter_content(1024 * 1024), total=audio_size, desc="正在下音频",
                              unit="MB"):
                fp.write(audio)

        v = self.FILE + video_info[0] + "_video.flv"
        a = self.FILE + video_info[0] + "_audio.flv"

        vf = ffmpeg.input(v)
        af = ffmpeg.input(a)

        output = ffmpeg.output(vf, af, self.FILE + video_info[0] + ".mp4", r=60)
        ffmpeg.run(
            output,
            capture_stdout=True,
            capture_stderr=True,
            overwrite_output=True,
            cmd=self.FFMPEG
        )

        os.remove(v)
        os.remove(a)


class UserDataSpider:
    """
    up投稿视频信息
    """

    def __init__(self, mid):
        self.MID = mid
        self.SALT = "ea1db124af3c7062474693fa704f4ff8"
        self.USER_URL = "https://api.bilibili.com/x/space/wbi/arc/search?"
        self.HEADERS = {
            "Referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        }
        self.CK = dict()
        self.CK["SESSDATA"] = session
        self.FILE = open("./result/BV.txt", "a+", encoding="utf-8")

    def get_md5(self, params):
        """
        获取md5值加密参数
        :return: w_rid
        """
        m = hashlib.md5((params + self.SALT).encode("utf-8"))

        return m.hexdigest()

    def get_video_list(self):
        """
        获取某一个up主的全部投稿视频BV号
        :return: video_data
        """
        params = {
            "mid": self.MID,
            "ps": 30,
            "tid": 0,
            "pn": 1,
            "keyword": "",
            "order": "pubdate",
            "platform": "web",
            "web_location": 1550101,
            "order_avoided": "true",
            "wts": int(time.time())
        }
        params["w_rid"] = self.get_md5(urlencode(params))

        response = requests.get(self.USER_URL, headers=self.HEADERS, params=params, cookies=self.CK)
        count = response.json()["data"]["page"]["count"]
        page = int(count / 30 + 1)

        for pn in range(1, page+1):
            print("pn:", pn)
            try:
                params = {
                    "mid": self.MID,
                    "ps": 30,
                    "tid": 0,
                    "pn": pn,
                    "keyword": "",
                    "order": "pubdate",
                    "platform": "web",
                    "web_location": 1550101,
                    "order_avoided": "true",
                    "wts": int(time.time())
                }
                params["w_rid"] = self.get_md5(urlencode(params))
                resp = requests.get(self.USER_URL, headers=self.HEADERS, params=params, cookies=self.CK)
                for data in resp.json()["data"]["list"]["vlist"]:
                    print(data["title"])
                    print(data["bvid"])
                    self.FILE.write(data["title"]+"\t"+data["bvid"]+"\n")
            except Exception as e:
                print(repr(e))

            time.sleep(random.randint(4,7))


if __name__ == '__main__':
    # up主的id
    user_id = "244951884"
    BV = "BV17V411G7rw"
    session = "xxx"

    # UserSpider = UserDataSpider(user_id)
    # UserSpider.get_video_list()

    VideoSpider = BILIBILIVideoSpider(session, BV)
    VideoSpider.download()
