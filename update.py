#!/usr/bin/python

import argparse
import sqlite3
import logging

from sqldb.dao import DAO
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
    parser.add_argument('set_code', help='three-letter code of set to add or update (e.g., "ORI")')
    parser.add_argument('set_name', nargs='?', help='name of set to add or update (e.g., "Magic Origins")')
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
    logging.basicConfig(filename=".update.%s.log" % args.set_code, filemode="w", level=logging.DEBUG)
    scraper = SetScraper(args.set_code, args.set_name, langs)
    db = scraper.scrape()
    conn = sqlite3.connect(args.file)
    create_tables(conn)
    with conn:
        sdao = SetDAO(args.set_code, args.set_name, conn)
        sdao.save()
        with conn:
            for k, v in db.iteritems():
                cdao = CardDAO(v, conn)
                cdao.save()
    set_count = conn.execute("select count(*) from Cards where set_code = ?", (args.set_code,)).fetchone()[0]
    new_count = conn.execute("select count(*) from Cards where set_code = ? and equivalent_to is null", (args.set_code,)).fetchone()[0]
    phy_count = conn.execute("select count(*) from Cards where set_code = ? and equivalent_to is null and back_face_of is null", (args.set_code,)).fetchone()[0]
    all_count = conn.execute("select count(*) from Cards").fetchone()[0]
    conn.close()
    print "Records:"
    print "  inserted:  %d" % DAO.inserted
    print "  updated:   %d" % DAO.updated
    print "  unchanged: %d" % DAO.unchanged
    print "Cards:"
    print "  %d printings in set %s" % (set_count, args.set_code)
    print "  %d new cards in set %s" % (new_count, args.set_code)
    print "  %d of which physically collectible" % phy_count
    print "  %d printings total" % all_count


if __name__ == "__main__":
    main()
