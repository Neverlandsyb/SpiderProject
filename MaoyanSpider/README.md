1.思路：先请求经典影片得到电影的id，遍历id的列表，将参数进行构造获得params请求详情页，再翻页继续请求

2.解密：ts（时间戳）、index（10以内的随机数）、u（固参）、c（部分固参+前面两参数），signKey（c+u然后再md5进行加密）,可直接扣JS代码获取params

3.注意：a.在经典影片页面headers必须得带Set-Cookie字段；b.电影的详情页面必须得带上uuid；c.可以不登陆，但过快请求需ip代理，不然容易出验证，而且翻页到一定数量会需要登录
