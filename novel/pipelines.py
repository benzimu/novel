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
import time


class FormatDataPipeline(object):
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

        chapter_item = item.get('chapter_item', None)
        if chapter_item:
            if not chapter_item.get('res_id', None):
                chapter_item['res_id'] = ''

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
            chapter_item = item.get('chapter_item', None)

            query_novel_detail_id = self.dbpool.runInteraction(self._query_novel_detail_id, novel_item)
            # query_novel_detail_id.addCallback(self._insert_or_update_novel_detail, novel_item, chapter_item)

            # query_novel_detail = self.dbpool.runInteraction(self._insert_novel_detail, novel_item)
            # query_novel_detail.addErrback(self._handle_error, item, spider)
            #
            # time.sleep(5)

            # query_novel_detail_id = self.dbpool.runInteraction(self._query_novel_detail_id, novel_item)

            query_novel_detail_id.addCallback(self._query_novel_handler, chapter_item, novel_item)
            query_novel_detail_id.addErrback(self._handle_error, item, spider)

            return query_novel_detail_id
        except Exception as e:
            logging.error('#####SaveDattabasePipeline:process_item():e:{0}#####'.format(e))
            logging.error(traceback.print_exc())
            raise e

    def _query_novel_handler(self, result, chapters_item, novel_item):
        logging.info('#####SaveDatabasePipeline:_query_novel_handler()#####')
        if not result:
            insert_novel_detail = self.dbpool.runInteraction(self._insert_novel_detail, novel_item)
            insert_novel_detail.addErrback(self._handle_error, novel_item)

            time.sleep(5)

            query_novel_detail_id = self.dbpool.runInteraction(self._query_novel_detail_id, novel_item)
            query_novel_detail_id.addCallback(self._insert_novel_chapters_handler, chapters_item)
            query_novel_detail_id.addErrback(self._handle_error, chapters_item)
        else:
            update_novel_detail = self.dbpool.runInteraction(self._update_novel_detail, result[0], novel_item)
            update_novel_detail.addErrback(self._handle_error, novel_item)

            time.sleep(5)

            chapters_item['novel_detail_id'] = result[0]
            query_novel_chapters = self.dbpool.runInteraction(self._query_novel_chapters, chapters_item)
            query_novel_chapters.addCallback(self._insert_novel_chapters_handler2, chapters_item)

    def _insert_novel_chapters_handler(self, result, chapters_item):
        if result:
            chapters_item['novel_detail_id'] = result[0]

            query_novel_chapters = self.dbpool.runInteraction(self._query_novel_chapters, chapters_item)
            query_novel_chapters.addCallback(self._insert_novel_chapters_handler2, chapters_item)

    def _insert_novel_chapters_handler2(self, result, chapters_item):
        if not result:
            insert_novel_chapters = self.dbpool.runInteraction(self._insert_novel_chapters, chapters_item)
            insert_novel_chapters.addErrback(self._handle_error, chapters_item)

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

    def _update_novel_detail(self, tx, id, item):
        try:
            logging.info('#####SaveDatabasePipeline:_update_novel_detail()#####')
            logging.info('#####SaveDatabasePipeline:_update_novel_detail():tx info: {0}'.format(tx))
            insert_sql = "update novel_detail set res_id=%s, name=%s, author=%s, author_href=%s, picture=%s, " \
                         "update_time=%s, status=%s, type=%s, type_href=%s, source=%s, description=%s, " \
                         "latest_chapters=%s, chapters_categore_href=%s where id=%s"
            logging.info('#####SaveDatabasePipeline:_update_novel_detail():insert_sql info: {0}#####'.format(insert_sql))

            params = (item['res_id'], item['name'], item['author'], item['author_href'], item['picture'],
                      item['update_time'], item['status'], item['type'], item['type_href'], item['source'],
                      item['description'], item['latest_chapters'], item['chapters_categore_href'], id)
            logging.info('#####SaveDatabasePipeline:_update_novel_detail():params info: {0}#####'.format(params))

            res = tx.execute(insert_sql, params)
            logging.info('#####SaveDatabasePipeline:_update_novel_detail():res info:{0}#####'.format(res))
        except Exception as e:
            logging.error('#####SaveDattabasePipeline:_update_novel_detail():e:{0}#####'.format(e))
            logging.error(traceback.print_exc())
            raise e

    def _query_novel_detail_id(self, tx, item):
        try:
            logging.info('#####SaveDatabasePipeline:_query_novel_detail_id()#####')
            query_sql = "select * from novel_detail where name = %s and author = %s"
            logging.info(
                '#####SaveDatabasePipeline:_query_novel_detail_id():query_sql info: {0}#####'.format(query_sql))

            params = (item['name'], item['author'])
            logging.info('#####SaveDatabasePipeline:_query_novel_detail_id():params info: {0}#####'.format(params))

            tx.execute(query_sql, params)

            res = tx.fetchall()
            logging.info('#####SaveDatabasePipeline:_query_novel_detail_id():res info:{0}#####'.format(res))
            if res:
                return res[0]
            else:
                return None

        except Exception as e:
            logging.error('#####SaveDattabasePipeline:_query_novel_detail_id():e:{0}#####'.format(e))
            logging.error(traceback.print_exc())
            raise e

    def _insert_novel_chapters(self, tx, item):
        try:
            logging.info('#####SaveDatabasePipeline:_insert_novel_chapters()#####')
            logging.info('#####SaveDatabasePipeline:_insert_novel_chapters():tx info: {0}'.format(tx))
            insert_sql = "insert into novel_chapters(res_id, novel_detail_id, source, counts, name, content) " \
                         "values(%s, %s, %s, %s, %s, %s)"
            logging.info('#####SaveDatabasePipeline:_insert_novel_chapters():insert_sql info: {0}#####'.format(insert_sql))

            params = (item['res_id'], item['novel_detail_id'], item['source'], item['counts'],
                      item['name'], item['content'])
            logging.info('#####SaveDatabasePipeline:_insert_novel_chapters():params info: {0}#####'.format(params))

            res = tx.execute(insert_sql, params)
            logging.info('#####SaveDatabasePipeline:_insert_novel_chapters():res info:{0}#####'.format(res))
        except Exception as e:
            logging.error('#####SaveDattabasePipeline:_insert_novel_chapters():e:{0}#####'.format(e))
            logging.error(traceback.print_exc())
            raise e

    def _query_novel_chapters(self, tx, item):
        try:
            logging.info('#####SaveDatabasePipeline:_query_novel_chapters()#####')
            logging.info('#####SaveDatabasePipeline:_query_novel_chapters():tx info: {0}'.format(tx))
            insert_sql = "select * from novel_chapters where counts=%s and name=%s"
            logging.info('#####SaveDatabasePipeline:_query_novel_chapters():insert_sql info: {0}#####'.format(insert_sql))

            params = (item['counts'], item['name'])
            logging.info('#####SaveDatabasePipeline:_query_novel_chapters():params info: {0}#####'.format(params))

            tx.execute(insert_sql, params)
            res = tx.fetchall()
            logging.info('#####SaveDatabasePipeline:_query_novel_detail_id():res info:{0}#####'.format(res))
            if res:
                return res[0]
            else:
                return None
        except Exception as e:
            logging.error('#####SaveDattabasePipeline:_query_novel_chapters():e:{0}#####'.format(e))
            logging.error(traceback.print_exc())
            raise e

    def _handle_error(self, failue, item=None, spider=None):
        logging.info('#####SaveDatabasePipeline:_handle_error()#####')
        logging.error('#####SaveDatabasePipeline:_handle_error():failue info:{0}#####'.format(failue))
