# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NovelItem(scrapy.Item):
    id = scrapy.Field()                         # 索引ID
    res_id = scrapy.Field()                     # 原始ID
    name = scrapy.Field()                       # 小说名
    author = scrapy.Field()                     # 作者
    author_href = scrapy.Field()                # 作者详情链接
    picture = scrapy.Field()                    # 图片
    update_time = scrapy.Field()                # 小说更新时间
    status = scrapy.Field()                     # 状态：连载中、已完结、、、
    type = scrapy.Field()                       # 类型：玄幻、都市、、、
    type_href = scrapy.Field()                  # 类型详情链接
    source = scrapy.Field()                     # 来源
    description = scrapy.Field()                # 描述
    latest_chapters = scrapy.Field()            # 最新章节,最新章节,用于判断是否与数据库数据同步
    chapters_categore_href = scrapy.Field()     # 章节目录详情链接


class ChaptersItem(scrapy.Item):
    id = scrapy.Field()                         # 索引ID
    res_id = scrapy.Field()                     # 原始ID
    novel_detail_id = scrapy.Field()            # 小说ID
    source = scrapy.Field()                     # 来源
    counts = scrapy.Field()                     # 章数
    name = scrapy.Field()                       # 章名
    content = scrapy.Field()                    # 章节内容

