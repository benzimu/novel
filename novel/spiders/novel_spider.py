#!/usr/bin/env python
#  -*- coding:utf-8 -*-

"""
@author: ben
@time: 4/11/17
@desc: 
"""

import scrapy
import logging
from novel.items import NovelItem


class NovelSpider(scrapy.Spider):
    name = 'novel'
    allowed_domains = ['book.easou.com']
    start_urls = ['http://book.easou.com/w/novel/18670767/0.html']

    # def start_requests(self):
    #     pass

    def parse(self, response):
        logging.info('start parse')

        base_href = 'http://book.easou.com'

        novelitem = NovelItem()

        content = response.xpath("//div[@class='content']/div")
        print content[0]
        novelitem['picture'] = content[0].xpath(u"//img[@alt='一念永恒']/@src").extract()[0]
        novelitem['name'] = content[0].xpath("//div[@class='tit']/h1/text()").extract()[0]
        novelitem['status'] = content[0].xpath("//div[@class='tit']/span/text()").extract()[0]
        novelitem['author'] = content[0].xpath("//div[@class='author']//a/text()").extract()[0]
        novelitem['author_href'] = base_href + content[0].xpath("//div[@class='author']//a/@href").extract()[0]
        novelitem['type'] = content[0].xpath("//div[@class='kind']//a/text()").extract()[0]
        novelitem['type_href'] = base_href + content[0].xpath("//div[@class='kind']//a/@href").extract()[0]
        novelitem['update_time'] = content[0].xpath("//div[@class='updateDate']/span/text()").extract()[0]
        novelitem['source'] = content[0].xpath("//div[@class='source']/span/text()").extract()[0]
        novelitem['description'] = content[0].xpath("//div[@class='desc']/text()").extract()[0]
        novelitem['latest_chapters'] = content[0].xpath("//div[@class='last']/a/text()").extract()[0]
        novelitem['latest_chapters_href'] = base_href + content[0].xpath("//div[@class='last']/a/@href").extract()[0]

        print novelitem
