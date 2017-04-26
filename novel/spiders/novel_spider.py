#!/usr/bin/env python
#  -*- coding:utf-8 -*-

"""
@author: ben
@time: 4/11/17
@desc: 
"""

import scrapy
import logging
import json
from novel.items import NovelItem
from novel.items import ChaptersItem

from novel.utils.UrlParse import get_domain
from novel.utils.Constant import Constant


class NovelSpider(scrapy.Spider):

    name = 'novel'
    allowed_domains = ['book.easou.com']
    start_urls = ['http://book.easou.com/w/novel/18670767/0.html']
        # , 'http://book.easou.com/w/novel/16120847/0.html']

    # def start_requests(self):
    #     user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 \
    #                              Safari/537.36 SE 2.X MetaSr 1.0'
    #     headers = {'User-Agent': user_agent}
    #     yield scrapy.Request(url=self.start_urls[0], method='GET', headers=headers, callback=self.parse)

    def parse(self, response):
        logging.info('#####NovelSpider:parse()#####')

        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 \
                                         Safari/537.36 SE 2.X MetaSr 1.0'
        headers = {'User-Agent': user_agent}

        novelitem = NovelItem()

        content = response.xpath("//div[@class='content']/div")

        novelitem['picture'] = content[0].xpath("//div[@class='imgShow']/img/@src").extract()[0]
        novelitem['name'] = content[0].xpath("//div[@class='tit']/h1/text()").extract()[0].strip()
        novelitem['status'] = content[0].xpath("//div[@class='tit']/span/text()").extract()[0].strip()
        novelitem['author'] = content[0].xpath("//div[@class='author']//a/text()").extract()[0].strip()
        novelitem['author_href'] = content[0].xpath("//div[@class='author']//a/@href").extract()[0]
        novelitem['type'] = content[0].xpath("//div[@class='kind']//a/text()").extract()[0].strip()
        novelitem['type_href'] = content[0].xpath("//div[@class='kind']//a/@href").extract()[0]
        novelitem['update_time'] = content[0].xpath("//div[@class='updateDate']/span/text()").extract()[0]
        novelitem['source'] = content[0].xpath("//div[@class='source']/span/text()").extract()[0].strip()
        novelitem['description'] = content[0].xpath("//div[@class='desc']/text()").extract()[0].strip()
        novelitem['latest_chapters'] = content[0].xpath("//div[@class='last']/a/text()").extract()[0].strip().split(' ')[1]
        novelitem['chapters_categore_href'] = content[0].xpath("//div[@class='allcategore']//a/@href").extract()[0]

        logging.info('#####NovelSpider:parse():novelitem info:{0}#####'.format(novelitem))

        yield scrapy.Request('http://book.easou.com' + novelitem['chapters_categore_href'], method='GET',
                             headers=headers, callback=self.chapters_categore, meta={'novel_detail': novelitem})

    def chapters_categore(self, response):
        logging.info('#####NovelSpider:chapters_categore():response info:{0}#####'.format(response))

        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 \
                                                 Safari/537.36 SE 2.X MetaSr 1.0'
        headers = {'User-Agent': user_agent}

        categores_hrefs = response.xpath("//div[@class='category']/ul//a/@href").extract()
        print '--------------categores_hrefs_5', categores_hrefs
        # 第一次爬取所有的数据，接下来每次爬取最后五条数据
        categores_hrefs = categores_hrefs[-5:]
        print '--------------categores_hrefs_5', categores_hrefs
        for c_item in categores_hrefs:
            yield scrapy.Request('http://book.easou.com' + c_item, headers=headers, callback=self.chapters_detail,
                                 meta={'novel_detail': response.meta['novel_detail']})

    def chapters_detail(self, response):
        logging.info('#####NovelSpider:chapters_detail():response info:{0}#####'.format(response))

        novel_item = response.meta['novel_detail']

        chapter_item = ChaptersItem()
        chapter_item['source'] = response.url

        source_domain = get_domain(chapter_item['source'])
        logging.info('#####NovelSpider:chapters_detail():source_domain info:{0}#####'.format(source_domain))
        if not source_domain:
            logging.error("#####NovelSpider:chapters_detail():爬取数据链接出错,请检查小说章节详情链接:{0}".format(chapter_item['source']))
            return

        if source_domain == Constant.SOURCE_DOMAIN['DUXS']:
            counts_name = response.xpath("//div[@class='content']//h1/text()").extract()[0].strip().split(' ')
            chapter_item['counts'] = counts_name[0]
            chapter_item['name'] = counts_name[1]
            chapter_item['content'] = ''.join(response.xpath("//div[@class='chapter-content']/node()").extract()).strip()
        elif source_domain == Constant.SOURCE_DOMAIN['ASZW']:
            counts_name = response.xpath("//div[@class='bdb']/h1/text()").extract()[0].strip().split(' ')
            if len(counts_name) == 2:
                chapter_item['counts'] = counts_name[0]
                chapter_item['name'] = counts_name[1]
            elif len(counts_name) == 3:
                chapter_item['counts'] = counts_name[1]
                chapter_item['name'] = counts_name[2]
            chapter_item['content'] = json.dumps(response.xpath("//div[@id='contents']/text()").extract()[0].strip())
        elif source_domain == Constant.SOURCE_DOMAIN['BQG']:
            counts_name = response.xpath("//div[@class='bookname']/h1/text()").extract()[0].strip().split(' ')
            chapter_item['counts'] = counts_name[0]
            chapter_item['name'] = counts_name[1]
            chapter_item['content'] = ''.join(response.xpath("//div[@id='content']/node()").extract()).strip()
        elif source_domain == Constant.SOURCE_DOMAIN['BQW']:
            counts_name = response.xpath("//div[@class='read_title']/h1/text()").extract()[0].strip().split(' ')
            chapter_item['counts'] = counts_name[0]
            chapter_item['name'] = counts_name[1]
            chapter_item['content'] = ''.join(response.xpath("//div[@class='content']/node()").extract()).strip()
        elif source_domain == Constant.SOURCE_DOMAIN['ZW']:
            counts_name = response.xpath("//div[@class='bdsub']//dd[0]/h1/text()").extract()[0].strip().split(' ')
            chapter_item['counts'] = counts_name[0]
            chapter_item['name'] = counts_name[1]
            chapter_item['content'] = ''.join(response.xpath("//div[@class='bdsub']//dd[@id='contents']/node()").extract()).strip()
        elif source_domain == Constant.SOURCE_DOMAIN['GLW']:
            pass
        elif source_domain == Constant.SOURCE_DOMAIN['SW']:
            counts_name = response.xpath("//div[@class='bookname']/h1/text()").extract()[0].strip().split(' ')
            if len(counts_name) == 2:
                chapter_item['counts'] = counts_name[0]
                chapter_item['name'] = counts_name[1]
            elif len(counts_name) == 3:
                chapter_item['counts'] = counts_name[1]
                chapter_item['name'] = counts_name[2]
            chapter_item['content'] = ''.join(response.xpath("//div[@class='content']/node()").extract()).strip()
        elif source_domain == Constant.SOURCE_DOMAIN['QL']:
            counts_name = response.xpath("//div[@class='bookname']/h1/text()").extract()[0].strip().split(' ')
            if len(counts_name) == 2:
                chapter_item['counts'] = counts_name[0]
                chapter_item['name'] = counts_name[1]
            elif len(counts_name) == 3:
                chapter_item['counts'] = counts_name[1]
                chapter_item['name'] = counts_name[2]
            chapter_item['content'] = ''.join(response.xpath("//div[@id='content']/node()").extract()).strip()
        else:
            logging.error("#####NovelSpider:chapters_detail():没有此域名网站爬取模板，请联系管理员！:{0}".format(chapter_item['source']))
            return
        yield {'novel_item': novel_item, 'chapter_item': chapter_item}



