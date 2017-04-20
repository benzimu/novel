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
        logging.info('#####HrefPipeline:process_item():item info: {0}#####'.format(item))

        novel_item = item.get('novel_item', None)
        if novel_item:
            if novel_item['author_href']:
                novel_item['author_href'] = self.base_domain + novel_item['author_href']
            if novel_item['type_href']:
                novel_item['type_href'] = self.base_domain + novel_item['type_href']
            if not novel_item.get('res_id', None):
                novel_item['res_id'] = ''

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
        try:
            logging.info('#####SaveDatabasePipeline:process_item()#####')

            novel_item = item.get('novel_item', None)
            chapter_item = item.get('novel_item', None)

            # query_novel_detail = self.dbpool.runInteraction(self._insert_novel_detail, novel_item)
            # query_novel_detail.addErrback(self._handle_error, item, spider)

            query_novel_detail_id = self.dbpool.runInteraction(self._query_novel_detail_id, novel_item)
            # print '++++++++++++++++:', type(query_novel_detail_id)
            # print '++++++++++++++++:', dir(query_novel_detail_id)
            # print '++++++++++++++++:', query_novel_detail_id

            query_novel_detail_id.addCallback(self._test)
            query_novel_detail_id.addErrback(self._handle_error, item, spider)
            # print 'query_novel_detail_id:', query_novel_detail_id
            # query_novel_detail_id.addErrback(self._handle_error, item, spider)

            return query_novel_detail_id
        except Exception as e:
            logging.error('#####SaveDattabasePipeline:process_item():e:{0}#####'.format(e))
            logging.error(traceback.print_exc())
            raise e

    def _test(self, result):
        print '---------------_test()'
        print '-------------result:', result

    def _insert_novel_detail(self, tx, item):
        try:
            logging.info('#####SaveDatabasePipeline:_insert_novel_detail()#####')
            logging.info('#####SaveDatabasePipeline:_insert_novel_detail():tx info: {0}'.format(tx))
            insert_sql = "insert into novel_detail(res_id, name, author, author_href, picture, update_time, status, " \
                         "type, type_href, source, description, latest_chapters, chapters_categore_href) " \
                         "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            logging.info('#####SaveDatabasePipeline:_insert_novel_detail():insert_sql info: {0}#####'.format(insert_sql))

            params = (item['res_id'], item['name'], item['author'], item['author_href'], item['picture'],
                      item['update_time'], item['status'], item['type'], item['type_href'], item['source'],
                      item['description'], item['latest_chapters'], item['chapters_categore_href'])
            logging.info('#####SaveDatabasePipeline:_insert_novel_detail():params info: {0}#####'.format(params))

            res = tx.execute(insert_sql, params)
            logging.info('#####SaveDatabasePipeline:_insert_novel_detail():res info:{0}#####'.format(res))
        except Exception as e:
            logging.error('#####SaveDattabasePipeline:_insert_novel_detail():e:{0}#####'.format(e))
            logging.error(traceback.print_exc())
            raise e

    def _query_novel_detail_id(self, tx, item):
        try:
            logging.info('#####SaveDatabasePipeline:_query_novel_detail_id()#####')
            query_sql = "select id from novel_detail where name = %s and author = %s"
            logging.info(
                '#####SaveDatabasePipeline:_query_novel_detail_id():query_sql info: {0}#####'.format(query_sql))

            params = (item['name'], item['author'])
            logging.info('#####SaveDatabasePipeline:_query_novel_detail_id():params info: {0}#####'.format(params))

            tx.execute(query_sql, params)

            res = tx.fetchall()
            logging.info('#####SaveDatabasePipeline:_query_novel_detail_id():res info:{0}#####'.format(res))
            if res:
                print res[0][0]
                return res[0][0]
            else:
                return None

        except Exception as e:
            logging.error('#####SaveDattabasePipeline:_query_novel_detail_id():e:{0}#####'.format(e))
            logging.error(traceback.print_exc())
            raise e

    def _insert_novel_chapters(self, tx, item):
        try:
            logging.info('#####SaveDatabasePipeline:_insert_novel_detail()#####')
            logging.info('#####SaveDatabasePipeline:_insert_novel_detail():tx info: {0}'.format(tx))
            insert_sql = "insert into novel_detail(res_id, name, author, author_href, picture, update_time, status, " \
                         "type, type_href, source, description, latest_chapters, chapters_categore_href) " \
                         "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            logging.info('#####SaveDatabasePipeline:_insert_novel_detail():insert_sql info: {0}#####'.format(insert_sql))

            params = (item['res_id'], item['name'], item['author'], item['author_href'], item['picture'],
                      item['update_time'], item['status'], item['type'], item['type_href'], item['source'],
                      item['description'], item['latest_chapters'], item['chapters_categore_href'])
            logging.info('#####SaveDatabasePipeline:_insert_novel_detail():params info: {0}#####'.format(params))

            res = tx.execute(insert_sql, params)
            logging.info('#####SaveDatabasePipeline:_insert_novel_detail():res info:{0}#####'.format(res))
        except Exception as e:
            logging.error('#####SaveDattabasePipeline:_insert_novel_detail():e:{0}#####'.format(e))
            logging.error(traceback.print_exc())
            raise e

    def _handle_error(self, failue, item, spider):
        logging.info('#####SaveDatabasePipeline:_handle_error()#####')
        logging.error('#####SaveDatabasePipeline:_handle_error():failue info:{0}#####'.format(failue))
