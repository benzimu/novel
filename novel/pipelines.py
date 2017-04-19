# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import MySQLdb
from twisted.enterprise import adbapi
import logging
import traceback


class HrefPipeline(object):
    def __init__(self):
        self.base_domain = 'http://book.easou.com'

    def process_item(self, item, spider):
        logging.info('#####HrefPipeline:process_item()#####')
        if item['author_href']:
            item['author_href'] = self.base_domain + item['author_href']
        if item['type_href']:
            item['type_href'] = self.base_domain + item['type_href']
        if item['latest_chapters_href']:
            item['latest_chapters_href'] = self.base_domain + item['latest_chapters_href']
        if not item.get('res_id', None):
            item['res_id'] = ''
        return item


class SaveDatabasePipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        logging.info('#####SaveDatabasePipeline:from_settings()#####')
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            port=settings['MYSQL_PORT'],
            db=settings['MYSQL_DATABASE'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',
            use_unicode=False
        )
        logging.info('#####SaveDatabasePipeline:from_settings():dbparams info : {0}'.format(dbparams))

        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        logging.info('#####SaveDatabasePipeline:process_item()#####')
        query = self.dbpool.runInteraction(self._insert_data, item)
        query.addErrback(self._handle_error, item, spider)
        return item

    def _insert_data(self, tx, item):
        try:
            logging.info('#####SaveDatabasePipeline:_insert_data()#####')
            logging.info('#####SaveDatabasePipeline:_insert_data():tx info: {0}'.format(tx))
            insert_sql = "insert into novel_detail(res_id, name, author, author_href, picture, update_time, status, " \
                         "type, type_href, source, description, latest_chapters, latest_chapters_href) " \
                         "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            logging.info('#####SaveDatabasePipeline:_insert_data():insert_sql info: {0}#####'.format(insert_sql))

            params = (item['res_id'], item['name'], item['author'], item['author_href'], item['picture'],
                      item['update_time'], item['status'], item['type'], item['type_href'], item['source'],
                      item['description'], item['latest_chapters'], item['latest_chapters_href'])
            logging.info('#####SaveDatabasePipeline:_insert_data():params info: {0}#####'.format(params))

            res = tx.execute(insert_sql, params)
            print '---------------', res
        except Exception as e:
            logging.error('#####SaveDatabasePipeline:_insert_data():e:{0}#####'.format(e))
            logging.error(traceback.print_exc())

    def _handle_error(self, failue, item, spider):
        logging.info('#####SaveDatabasePipeline:_handle_error()#####')
        logging.error('#####SaveDatabasePipeline:_handle_error():failue info:{0}#####'.format(failue))
