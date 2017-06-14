#!/usr/bin/env python
#  -*- coding:utf-8 -*-

"""
@author: ben
@time: 4/11/17
@desc: 
"""

import scrapy
import logging
import os
import json
import time
import MySQLdb

from novel.items import NovelItem
from novel.items import ChaptersItem
from novel import settings

from novel.utils.UrlParse import get_domain
from novel.utils.Constant import Constant


class NovelSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        dbparams = dict(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            db=settings.MYSQL_DATABASE,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWORD,
            charset='utf8',
            use_unicode=False
        )
        logging.info('#####NovelSpider:__init__():dbparams info : {0}'.format(dbparams))

        self.conn = MySQLdb.connect(**dbparams)

        super(NovelSpider, self).__init__(*args, **kwargs)

    name = 'novel'
    allowed_domains = settings.ALLOWED_DOMAINS
    start_urls = settings.START_URLS

    def parse(self, response):
        logging.info('#####NovelSpider:parse()#####')

        novelitem = NovelItem()

        content = response.xpath("//div[@id='centerm']//div[@id='content']")
        novelitem['picture'] = content[0].xpath(".//td[@width='80%' and @valign='top']//img/@src").extract()[0]
        novelitem['name'] = content[0].xpath(".//h1/text()").extract()[0].strip()
        td_selector = content[0].xpath(".//td")
        novelitem['status'] = td_selector[8].xpath("text()").extract()[0].strip().split(u'：')[1]
        novelitem['author'] = td_selector[4].xpath("text()").extract()[0].strip().split(u'：')[1]
        novelitem['type'] = td_selector[3].xpath("text()").extract()[0].strip().split(u'：')[1]
        novelitem['update_time'] = td_selector[7].xpath("text()").extract()[0].strip().split(u'：')[1]
        novelitem['description'] = content[0].xpath(".//td[@width='80%' and @valign='top']//text()").extract()[8].strip()
        novelitem['latest_chapters'] = content[0].xpath(".//td[@width='80%' and @valign='top']//text()").extract()[4].strip().split(' ')[1]
        novelitem['chapters_categore_href'] = content[0].xpath(".//caption//a/@href").extract()[0]

        logging.info('#####NovelSpider:parse():novelitem info:{0}#####'.format(novelitem))

        yield scrapy.Request(novelitem['chapters_categore_href'], method='GET',
                             callback=self.chapters_categore, meta={'novel_detail': novelitem})

    def chapters_categore(self, response):
        logging.info('#####NovelSpider:chapters_categore():response info:{0}#####'.format(response))

        url = response.url

        categores_hrefs = response.xpath("//div[@class='centent']//li/a/@href").extract()[4:]
        categores_names = response.xpath("//div[@class='centent']//li/a/text()").extract()[4:]

        logging.info('#####NovelSpider:chapters_categore():categores_hrefs info:{0}#####'.format(categores_hrefs))

        novel_detail = response.meta['novel_detail']

        cur = self.conn.cursor()

        query_resid_sql = "select name from novel_chapters where novel_detail_id = " \
                          "(select id from novel_detail where name=%s and author=%s)"
        params = (novel_detail['name'], novel_detail['author'])

        cur.execute(query_resid_sql, params)
        res = cur.fetchall()
        logging.info('#####NovelSpider:chapters_categore():res info:{0}#####'.format(res))
        if res:
            # 上一次爬取小说章节可能由于多种原因导致没有爬取下来，接下来每次爬取最新章节时重复爬取没有入库的章节
            res_names = [res_name[0] for res_name in res]
            categores_hrefs = [(i, categores_hrefs[i], categores_name) for i, categores_name in enumerate(categores_names)
                               if categores_name.encode("UTF-8") not in res_names]
            for i, c_item, categores_name in categores_hrefs:
                yield scrapy.Request(os.path.join(url.rsplit("/", 1)[0], c_item), callback=self.chapters_detail,
                                     meta={'novel_detail': novel_detail, 'chapter_name': categores_name,
                                           'chapter_index': i+1})
        else:
            for i, c_item in enumerate(categores_hrefs):
                yield scrapy.Request(os.path.join(url.rsplit("/", 1)[0], c_item), callback=self.chapters_detail,
                                     meta={'novel_detail': novel_detail, 'chapter_name': categores_names[i],
                                           'chapter_index': i+1})
        cur.close()

    def chapters_detail(self, response):
        logging.info('#####NovelSpider:chapters_detail():response info:{0}#####'.format(response))

        novel_item = response.meta['novel_detail']
        chapter_name = response.meta['chapter_name']
        chapter_index = response.meta['chapter_index']

        chapter_item = ChaptersItem()
        chapter_item['source'] = response.url
        source_domain = get_domain(chapter_item['source'])
        logging.info('#####NovelSpider:chapters_detail():source_domain info:{0}#####'.format(source_domain))
        if not source_domain:
            logging.error("#####NovelSpider:chapters_detail():爬取数据链接出错,请检查小说章节详情链接:{0}".format(chapter_item['source']))
            return

        chapter_item['name'] = chapter_name
        chapter_item['res_id'] = chapter_index

        # 获取节点之后的兄弟节点
        x = response.xpath(
            "//table[@align='center' and @border='0']/following-sibling::node()").extract()
        # 获取节点之前的兄弟节点
        y = response.xpath("//center[1]/preceding-sibling::node()").extract()
        # 获取两个集合的交集
        z = [_x for _x in x if _x in y]

        chapter_item['content'] = ''.join(z).strip()

        yield {'novel_item': novel_item, 'chapter_item': chapter_item}



