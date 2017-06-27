# 小说爬虫

## 项目简介

   基于scrapy框架的小说爬虫项目。  
   master分支主要爬取的是宜搜小说网的小说。
   由于宜搜网站崩溃，又有了新分支（piaotian），此分支主要爬取的是飘天文学网的小说（推荐使用此分支）。

## 使用方法

   可以在novel/settings.py文件中配置START_URLS，从而爬取你想要的小说。

## 运行环境：

   python2.7  
   scrapy==1.2.2  
   mysql5.7.17  

## 运行项目方法：
   
   1. 安装python2.7（linux系统内置，Windows百度）
   2. 使用pip安装依赖包：pip install scrapy==1.2.2
   3. 数据库初始化，sql脚本在script目录下
   4. 执行 python main.py