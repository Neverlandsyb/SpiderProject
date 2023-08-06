# SpiderProject

🚩[B站up主、视频爬虫](https://github.com/Neverlandsyb/SpiderProject/blob/main/BilibiliSpider)

1.解密：sign解密、BV号转AV号

2.UserDataSpider：up的视频BV号抓取

3.ffmpeg：将音频和视频合成一个MP4文件

4.BILIBILIVideoSpider：通过BV号抓取视频（有cookies才可抓高清，大会员可抓4K）

-------------------------------------------------------------------------------------------------------------------------

🚩[知乎类型id、问题、评论爬虫](https://github.com/Neverlandsyb/SpiderProject/blob/main/ZhihuSpider)

1.d_c0：cookies（建议随机cookies、IP代理）

2.get_headers：知乎请求头构造、[X-Zse-96.js](https://github.com/Neverlandsyb/SpiderProject/blob/main/ZhihuSpider/X-Zse-96.js)参数解密

3..get_type_id：知乎话题广场所有类型里的子id抓取、mysql入库

4.get_question、parser：知乎问题抓取（答案太多占内存懒得抓了）、数据解析

5.get_question_token_data：获取问题token以及其他信息（可根据token抓取评论，写了个demo但未更新完）

-------------------------------------------------------------------------------------------------------------------------

🚩[今日头条signature解密](https://github.com/Neverlandsyb/SpiderProject/blob/main/ToutiaoSpider)

1.[ToutiaoSign.py](https://github.com/Neverlandsyb/SpiderProject/blob/main/ToutiaoSpider/GetSign.py)：signature生成长短测试文件

2.[ToutiaoSign.js](https://github.com/Neverlandsyb/SpiderProject/blob/main/ToutiaoSpider/ToutiaoSign.js)：document.cookie是空则生成短signature、加入cookie则生成长signature

-------------------------------------------------------------------------------------------------------------------------

🚩[澎湃新闻爬虫](https://github.com/Neverlandsyb/SpiderProject/blob/main/PengpaiSpider)

1.nodeId：类型id（如：25429代表国际等）

2.crawler：根据时间戳从今天一直抓取到以前的所有新闻数据

3.date_to_timestamp、timestamp_to_date：时间戳和日期的相互转换

4.get_details、crawler：详情页抓取、数据解析（视频链接的新闻也存入json）

-------------------------------------------------------------------------------------------------------------------------

🚩[马蜂窝爬虫](https://github.com/Neverlandsyb/SpiderProject/blob/main/MafengwoSpider)

1.get_city_id：热门目的地id、景点id抓取

2.get_html：详情页、游记等等cookies解密

3.get_detail_data：抓取景点的详情写入json

4.get_params：_sn参数的md5解密，如果是抓取它其他页面只需要换参数即可

-------------------------------------------------------------------------------------------------------------------------

🚩[药智新闻爬虫](https://github.com/Neverlandsyb/SpiderProject/blob/main/YaozhiNewsSpider)

1.decrypt_data：请求获取加密的data信息、通过[YaozhiNewsDecrypt.js](https://github.com/Neverlandsyb/SpiderProject/blob/main/YaozhiNewsSpider/YaozhiNewsDecrypt.js)解密

2.如果在解密过程中遇见UnicodeDecodeError时，可根据 https://www.cnblogs.com/LoLong/p/17332908.html 文章进行修改即可

-------------------------------------------------------------------------------------------------------------------------

🚩[豆瓣搜索爬虫](https://github.com/Neverlandsyb/SpiderProject/blob/main/DoubanSpider)

1.rc4、_read_object：rc4算法解密

2.DoubanSpider：豆瓣原搜索 [api](https://search.douban.com/movie/subject_search?) 可不用登录搜索多页

3.参数：search_text（搜索文本）、start（页数，15的倍数）、cat固参

4.流程：获取搜索页面的源码取出其中的window_data加密数据，解密获取明文（最终得出的明文数据排序会随机打乱，需用正则取）

-------------------------------------------------------------------------------------------------------------------------

持续更新ing...
