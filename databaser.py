#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2015
import sqlite3

class Database():
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()

    def tables(self):
        expr = '''SELECT name FROM sqlite_master WHERE type='table';'''
        table_names = [t[0] for t in self.cur.execute(expr).fetchall()]
        return table_names

    def init_table(self, name, schema):
        schema_query = ', '.join((' ').join(column) for column in schema)
        if not name in self.tables():
            query = '''CREATE TABLE {table}({schema});'''
            query = query.format(table=name, schema=schema_query)
            self.cur.execute(query)
            self.conn.commit()

    def find_one(self, table, columns=None, **kwargs):
        if columns:
            columns = '{}'.format((', ').join(columns))
        else:
            columns = '*'
        filters = ' AND '.join(['{}=?'.format(col) for col in kwargs])
        values = kwargs.values()
        query = '''SELECT {cols} FROM {table} WHERE {filters};'''.format(
            cols=columns,
            table=table,
            filters=filters
            )
        result = self.cur.execute(query, values).fetchone()
        col_names = [d[0] for d in self.cur.description]
        if result:
            return dict(zip(col_names, result))
        else:
            return None

    def _row_formatter(self, row):
        cols, vals = [], []
        for col, val in row.items():           
            cols.append(col)
            vals.append(val)
        return cols, vals        

    def insert(self, table, row, replace=False):
        cols, vals = self._row_formatter(row)
        columns = (', ').join(cols)
        if replace:
            replace = ' OR REPLACE'
        else:
            replace = ''
        query = '''INSERT{replace} INTO {table} ({cols}) VALUES ({vals});'''.format(
            replace=replace,
            table=table,
            cols=columns,
            vals=','.join('?' * len(vals))
            )
        self.cur.execute(query, vals)
        self.conn.commit()

    def upsert(self, table, row, columns):
        filters = {c: row[c] for c in columns}
        existing_row = self.find_one(table, **filters)
        if existing_row:
            existing_row.update(row)
            updated_row = {k: v for k, v in existing_row.items() if v}
            rep = True
        else:
            updated_row = row
            rep = False
        self.insert(table, updated_row, replace=rep)

    def close(self):
        self.cur.close()
        self.conn.commit()
        self.conn.close()


if __name__ == '__main__':
    db = Database()
    row = {'id': 4920, 'price': '285', 'url': 'steve.com'}
    db.upsert('craigslist', row, ['id'])
    db.close()