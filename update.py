#!/usr/bin/python

import argparse
import sqlite3

from common.logger import Log
from sqldb.set_dao import SetDAO
from sqldb.card_dao import CardDAO
from scraper.languages import ALL_LANGS
from scraper.card import Card

def create_tables(conn):
    try:
        with conn:
            SetDAO.create_table(conn)
            CardDAO.create_table(conn)
    except sqlite3.OperationalError:
        pass


def set_has_cards(conn, set_id):
    cur = conn.execute('''SELECT * FROM Cards WHERE set_id = ?''', (set_id,))
    return cur.fetchone() is not None


def parse_args():
    parser = argparse.ArgumentParser(description='Create, udpate, or extend SQLite DB.')
    parser.add_argument('-f', '--file', default='magic.db', help='DB file to update')
    parser.add_argument('-l', '--lang', default='none', help='translations to udpate (none|all|de,fr ...)')
    parser.add_argument('-d', '--debug', action="store_true", help='print debug logs')
    parser.add_argument('-r', '--rm', action='store_true', help='delete set')
    parser.add_argument('set_id', help='Short ID of Magic set to add or update (e.g., "ORI")')
    parser.add_argument('set_name', nargs='?', help='full name of set to add or update (e.g., "Magic Origins")')
    args = parser.parse_args()
    langs = []
    if args.lang == 'all':
        langs = ALL_LANGS
    elif args.lang != 'none':
        langs = args.lang.split(',')
        for t in langs:
            if t not in ALL_LANGS:
                print 'Unknown language "%s".' % t
                sys.exit(2)
    return args, langs


def main():
    args, langs = parse_args()
    Log.log_level = Log.DEBUG if args.debug else Log.INFO
    conn = sqlite3.connect(args.file)
    create_tables(conn)
    s = SetDAO(args.set_id, args.set_name, conn)
    if args.rm:
        if set_has_cards(conn, s.id):
            Log.error("%s is not empty" % self)
        else:
            s.delete()
    else:
        s.save()
    c = Card()
    c.multiverseid = 17
    c.number = 12
    c.name = "Test Card"
    cdao = CardDAO(c, "ORI", conn)
    cdao.save()
    conn.close()


if __name__ == "__main__":
    main()
