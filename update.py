#!/usr/bin/python

import argparse
import sqlite3
import logging

from sqldb.set_dao import SetDAO
from sqldb.card_dao import CardDAO
from scraper.languages import ALL_LANGS
from scraper.card import Card
from scraper.scraper import SetScraper


def create_tables(conn):
    try:
        with conn:
            SetDAO.create_table(conn)
            CardDAO.create_table(conn)
    except sqlite3.OperationalError:
        pass


def parse_args():
    parser = argparse.ArgumentParser(description='Create, udpate, or extend SQLite DB.')
    parser.add_argument('-f', '--file', default='magic.db', help='DB file to update')
    parser.add_argument('-l', '--lang', default='none', help='translations to udpate (none|all|de,fr ...)')
    parser.add_argument('-r', '--rm', action='store_true', help='delete set')
    parser.add_argument('set_id', help='short name of Magic set to add or update (e.g., "ORI")')
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
    logging.basicConfig(filename=".update.log", filemode="w", level=logging.DEBUG)
    conn = sqlite3.connect(args.file)
    create_tables(conn)
    s = SetDAO(args.set_id, args.set_name, conn)
    if args.rm:
        with conn:
            CardDAO.delete_set(args.set_id, conn)
            s.delete()
    else:
        s.save()
        scraper = SetScraper(args.set_name, langs)
        db = scraper.scrape()
        with conn:
            for k, v in db.all_cards.iteritems():
                cdao = CardDAO(v, args.set_id, conn)
                cdao.save()
    count = conn.execute("select count(*) from Cards where set_id = ?", (args.set_id,)).fetchone()
    print "%d cards in set" % count
    count = conn.execute("select count(*) from Cards").fetchone()
    print "%d cards in database" % count
    conn.close()


if __name__ == "__main__":
    main()
