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
        logging.info('#####FormatDataPipeline:process_item():item info: {0}#####'.format(item))

        novel_item = item.get('novel_item', None)
        if novel_item:
            if not novel_item.get('res_id', None):
                novel_item['res_id'] = ''

        chapter_item = item.get('chapter_item', None)
        if chapter_item:
            if not chapter_item.get('counts', None):
                chapter_item['counts'] = ''

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

            query_novel_detail = self.dbpool.runInteraction(self._query_novel_detail_handler, novel_item)
            # 由于上一步操作是异步的，如果不设置等待时间，可能下一个请求过来时上一个插入还没有处理完，从而导致数据重复
            time.sleep(0.5)
            query_novel_detail.addCallback(self._insert_novel_chapters_handler, chapter_item)
            query_novel_detail.addErrback(self._handle_error, item, spider)

            return query_novel_detail
        except Exception as e:
            logging.error('#####SaveDattabasePipeline:process_item():e:{0}#####'.format(e))
            logging.error(traceback.print_exc())
            raise e

    def _insert_novel_chapters_handler(self, result, chapters_item):
        if result:
            chapters_item['novel_detail_id'] = result[0]

            query_novel_chapters = self.dbpool.runInteraction(self._query_novel_chapters, chapters_item)
            query_novel_chapters.addErrback(self._handle_error, chapters_item)

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
            update_sql = "update novel_detail set res_id=%s, name=%s, author=%s, author_href=%s, picture=%s, " \
                         "update_time=%s, status=%s, type=%s, type_href=%s, source=%s, description=%s, " \
                         "latest_chapters=%s, chapters_categore_href=%s where id=%s"
            logging.info('#####SaveDatabasePipeline:_update_novel_detail():insert_sql info: {0}#####'.format(update_sql))

            params = (item['res_id'], item['name'], item['author'], item['author_href'], item['picture'],
                      item['update_time'], item['status'], item['type'], item['type_href'], item['source'],
                      item['description'], item['latest_chapters'], item['chapters_categore_href'], id)
            logging.info('#####SaveDatabasePipeline:_update_novel_detail():params info: {0}#####'.format(params))

            res = tx.execute(update_sql, params)
            logging.info('#####SaveDatabasePipeline:_update_novel_detail():res info:{0}#####'.format(res))
        except Exception as e:
            logging.error('#####SaveDattabasePipeline:_update_novel_detail():e:{0}#####'.format(e))
            logging.error(traceback.print_exc())
            raise e

    def _query_novel_detail_handler(self, tx, item):
        try:
            logging.info('#####SaveDatabasePipeline:_query_novel_detail_handler()#####')
            query_sql = "select * from novel_detail where name = %s and author = %s"
            logging.info(
                '#####SaveDatabasePipeline:_query_novel_detail_handler():query_sql info: {0}#####'.format(query_sql))

            params = (item['name'], item['author'])
            logging.info('#####SaveDatabasePipeline:_query_novel_detail_handler():params info: {0}#####'.format(params))

            tx.execute(query_sql, params)

            res = tx.fetchall()
            logging.info('#####SaveDatabasePipeline:_query_novel_detail_handler():res info:{0}#####'.format(res))
            if not res:
                self._insert_novel_detail(tx, item)

                query_sql = "select * from novel_detail where name = %s and author = %s"
                params = (item['name'], item['author'])
                tx.execute(query_sql, params)
                res = tx.fetchall()
                return res[0]
            else:
                self._update_novel_detail(tx, res[0][0], item)
                return res[0]

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
            query_sql = "select * from novel_chapters where res_id=%s and novel_detail_id=%s"
            logging.info('#####SaveDatabasePipeline:_query_novel_chapters():query_sql info: {0}#####'.format(query_sql))

            params = (item['res_id'], item['novel_detail_id'])
            logging.info('#####SaveDatabasePipeline:_query_novel_chapters():params info: {0}#####'.format(params))

            tx.execute(query_sql, params)
            res = tx.fetchall()
            logging.info('#####SaveDatabasePipeline:_query_novel_detail_id():res info:{0}#####'.format(res))
            if not res:
                self._insert_novel_chapters(tx, item)
                return 0
            else:
                return res[0]
        except Exception as e:
            logging.error('#####SaveDattabasePipeline:_query_novel_chapters():e:{0}#####'.format(e))
            logging.error(traceback.print_exc())
            raise e

    def _handle_error(self, failue, item=None, spider=None):
        logging.info('#####SaveDatabasePipeline:_handle_error()#####')
        logging.error('#####SaveDatabasePipeline:_handle_error():failue info:{0}#####'.format(failue))
