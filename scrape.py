#!/usr/bin/python

import sys
import os
import argparse

from common.logger import Log
from scraper.scraper import SetScraper
from scraper.languages import ALL_LANGS


def parse_args():
    parser = argparse.ArgumentParser(description='Scrape gatherer for one set.')
    parser.add_argument('-l', '--lang', help='translations to scrape (none|all|de,fr ...)')
    parser.add_argument('-d', '--debug', action="store_true", help='print debug logs')
    parser.add_argument('set_name', help='full name of Magic set to add or update (e.g., "Magic Origins")')
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
    db = SetScraper(args.set_name, langs).scrape()

    print "=" * 80
    print "Final list:"
    print "=" * 80
    for card in db.check_list:
        print "%-50s%s" % (card, card.translations[langs[0]].name if langs else "")


if __name__ == "__main__":
    main()
