# novel
基于scrapy框架的小说爬虫项目。

master分支主要爬取的是宜搜小说网的小说。

由于宜搜网站崩溃，又有了新分支（piaotian），此分支主要爬取的是飘天文学网的小说。

可以在novel/settings.py文件中配置START_URLS，从而爬取你想要的小说。

运行环境：
    python2.7
    scrapy==1.2.2

运行项目方法：
    python main.py