# SpiderProject

🚩[B站up主、视频爬虫](https://github.com/Neverlandsyb/SpiderProject/blob/main/BilibiliSpider/BilibiliVideo.py)

1.sign解密、BV号转AV号

2.UserDataSpider：up的视频BV号抓取

3.ffmpeg：将音频和视频合成一个MP4文件

4.BILIBILIVideoSpider：通过BV号抓取视频（有cookies才可抓高清，大会员可抓4K）

-------------------------------------------------------------------------------------------------------------------------

🚩[知乎类型id、问题、评论爬虫](https://github.com/Neverlandsyb/SpiderProject/blob/main/ZhihuSpider/ZhihuContent.py)

1.d_c0：cookies（建议随机cookies、IP代理）

2.get_headers：知乎请求头构造、[X-Zse-96.js](https://github.com/Neverlandsyb/SpiderProject/blob/main/ZhihuSpider/X-Zse-96.js)参数解密

3..get_type_id：知乎话题广场所有类型里的子id抓取、mysql入库

4.get_question、parser：知乎问题抓取（答案太多占内存懒得抓了）、数据解析

5.get_question_token_data：获取问题token以及其他信息（可根据token抓取评论，写了个demo但未更新完）

-------------------------------------------------------------------------------------------------------------------------

🚩[今日头条signature解密](https://github.com/Neverlandsyb/SpiderProject/blob/main/ToutiaoSpider/GetSign.py)

1.[ToutiaoSign.py](https://github.com/Neverlandsyb/SpiderProject/blob/main/ToutiaoSpider/GetSign.py)：signature生成长短测试文件

2.[Sign.js](https://github.com/Neverlandsyb/SpiderProject/blob/main/ToutiaoSpider/Sign.js)：document.cookie是空则生成短signature、加入cookie则生成长signature

-------------------------------------------------------------------------------------------------------------------------


