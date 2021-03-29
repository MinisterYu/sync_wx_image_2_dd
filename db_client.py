# -*- coding: utf-8 -*-
# ! /usr/bin/env python
import sqlite3
import global_config


class DBClient:

    def __init__(self):
        self.logger = global_config.logger
        self.conn = None

    def connect(self):
        # sqlite3 设置
        self.conn = sqlite3.connect(global_config.DB_CONFIG, check_same_thread=False)
        return self.conn

    def dis_connect(self):
        self.conn.close()

    def do_insert(self, sql):
        try:
            conn = self.connect()
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            self.logger.error("insert sql: {0} met error: {1}".format(sql, e))
            raise e
        finally:
            self.dis_connect()

    def do_query(self, sql):
        try:
            conn = self.connect()
            cur = conn.cursor()
            result = cur.execute(sql)
            data = result.fetchall()
            cur.close()
            return data
        except Exception as e:
            self.logger.error("query sql: {0} met error: {1}".format(sql, e))
            raise e
        finally:
            self.dis_connect()

    def do_update(self, sql):
        try:
            conn = self.connect()
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            self.logger.error("do_update sql: {0} met error: {1}".format(sql, e))
            raise e
        finally:
            self.dis_connect()
